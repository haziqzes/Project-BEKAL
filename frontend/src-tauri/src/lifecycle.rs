use std::{
    env, fs,
    fs::OpenOptions,
    io::{Read, Write},
    net::{SocketAddr, TcpStream},
    path::{Path, PathBuf},
    process::{Command, Output},
    thread,
    time::Duration,
};

use tauri::Manager;

#[derive(Default)]
pub struct LifecycleState {
    runtime_root: Option<PathBuf>,
    owns_services: bool,
    shutdown_started: bool,
}

impl LifecycleState {
    pub fn start(&mut self, app: &tauri::AppHandle) -> Result<(), String> {
        let runtime_root = resolve_runtime_root(app)?;

        ensure_docker_available()?;

        let running_before = running_services(&runtime_root)?;

        let shared_session = running_before
            .iter()
            .any(|service| matches!(service.as_str(), "postgres" | "backend" | "frontend"));

        self.runtime_root = Some(runtime_root.clone());
        self.owns_services = !shared_session;

        let startup_result = (|| {
            checked_compose(
                &runtime_root,
                &["up", "-d", "--build", "postgres", "backend"],
                "start PostgreSQL and backend",
            )?;

            run_migrations(&runtime_root)?;

            wait_for_backend_health()?;

            Ok(())
        })();

        if let Err(error) = startup_result {
            if self.owns_services {
                let _ = compose(&runtime_root, &["stop", "backend", "postgres"]);
            }

            self.owns_services = false;
            return Err(error);
        }

        Ok(())
    }

    pub fn begin_shutdown(&mut self) -> bool {
        if self.shutdown_started {
            return false;
        }

        self.shutdown_started = true;
        true
    }

    pub fn shutdown(&mut self) {
        if !self.owns_services {
            return;
        }

        if let Some(runtime_root) = self.runtime_root.as_ref() {
            let _ = compose(runtime_root, &["stop", "backend", "postgres"]);
        }

        self.owns_services = false;
    }
}

fn resolve_runtime_root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    if let Some(explicit_root) = env::var_os("BEKAL_REPO_ROOT") {
        let path = PathBuf::from(explicit_root);

        if is_development_root(&path) {
            return Ok(path);
        }

        return Err(
            "BEKAL_REPO_ROOT does not contain docker-compose.yml, .env, backend and frontend."
                .to_string(),
        );
    }

    if let Ok(current_dir) = env::current_dir() {
        if let Some(root) = search_development_ancestors(&current_dir) {
            return Ok(root);
        }
    }

    if let Ok(executable) = env::current_exe() {
        if let Some(parent) = executable.parent() {
            if let Some(root) = search_development_ancestors(parent) {
                return Ok(root);
            }
        }
    }

    prepare_packaged_runtime(app)
}

fn search_development_ancestors(start: &Path) -> Option<PathBuf> {
    for ancestor in start.ancestors() {
        if is_development_root(ancestor) {
            return Some(ancestor.to_path_buf());
        }
    }

    None
}

fn is_development_root(path: &Path) -> bool {
    path.join("docker-compose.yml").is_file()
        && path.join(".env").is_file()
        && path.join("backend").is_dir()
        && path.join("frontend").is_dir()
}

fn prepare_packaged_runtime(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let resource_dir = app
        .path()
        .resource_dir()
        .map_err(|error| format!("Could not resolve BEKAL resource directory: {error}"))?;

    let template_root = resource_dir.join("generated-runtime");

    if !template_root.join("docker-compose.yml").is_file()
        || !template_root.join("backend").is_dir()
    {
        return Err(format!(
            "Packaged BEKAL runtime template is missing from {}",
            template_root.display()
        ));
    }

    let app_local_data = app
        .path()
        .app_local_data_dir()
        .map_err(|error| format!("Could not resolve BEKAL local data directory: {error}"))?;

    let runtime_root = app_local_data.join("runtime");

    fs::create_dir_all(&runtime_root).map_err(|error| {
        format!(
            "Could not create BEKAL runtime directory {}: {error}",
            runtime_root.display()
        )
    })?;

    sync_managed_tree(&template_root, &runtime_root)?;

    fs::create_dir_all(runtime_root.join("runtime-data")).map_err(|error| {
        format!(
            "Could not create BEKAL private runtime-data directory: {error}"
        )
    })?;

    ensure_runtime_env(&runtime_root)?;

    Ok(runtime_root)
}

fn sync_managed_tree(source: &Path, destination: &Path) -> Result<(), String> {
    for entry in fs::read_dir(source)
        .map_err(|error| format!("Could not read bundled runtime template: {error}"))?
    {
        let entry = entry.map_err(|error| format!("Could not read runtime entry: {error}"))?;
        let source_path = entry.path();
        let name = entry.file_name();
        let destination_path = destination.join(&name);
        let file_type = entry
            .file_type()
            .map_err(|error| format!("Could not inspect runtime entry: {error}"))?;

        if name == ".env" || name == "runtime-data" {
            continue;
        }

        if file_type.is_dir() {
            fs::create_dir_all(&destination_path).map_err(|error| {
                format!(
                    "Could not create managed runtime directory {}: {error}",
                    destination_path.display()
                )
            })?;

            sync_managed_tree(&source_path, &destination_path)?;
        } else if file_type.is_file() {
            fs::copy(&source_path, &destination_path).map_err(|error| {
                format!(
                    "Could not update managed runtime file {}: {error}",
                    destination_path.display()
                )
            })?;
        }
    }

    Ok(())
}

fn ensure_runtime_env(runtime_root: &Path) -> Result<(), String> {
    let env_path = runtime_root.join(".env");

    if env_path.is_file() {
        return Ok(());
    }

    let password = generate_local_password()?;
    let contents = format!(
        "POSTGRES_USER=bekal\nPOSTGRES_PASSWORD={password}\nPOSTGRES_DB=bekal\nBACKEND_PORT=8000\n"
    );

    let mut file = match OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&env_path)
    {
        Ok(file) => file,
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => return Ok(()),
        Err(error) => {
            return Err(format!(
                "Could not create private BEKAL runtime configuration {}: {error}",
                env_path.display()
            ));
        }
    };

    file.write_all(contents.as_bytes()).map_err(|error| {
        format!(
            "Could not write private BEKAL runtime configuration {}: {error}",
            env_path.display()
        )
    })
}

fn generate_local_password() -> Result<String, String> {
    #[cfg(target_os = "windows")]
    {
        for shell in ["powershell.exe", "pwsh.exe"] {
            let output = Command::new(shell)
                .args([
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "[guid]::NewGuid().ToString('N')",
                ])
                .output();

            if let Ok(output) = output {
                if output.status.success() {
                    let candidate = String::from_utf8_lossy(&output.stdout).trim().to_string();

                    if candidate.len() >= 32
                        && candidate.chars().all(|character| character.is_ascii_alphanumeric())
                    {
                        return Ok(candidate);
                    }
                }
            }
        }

        return Err(
            "Could not generate the private BEKAL database password with Windows PowerShell."
                .to_string(),
        );
    }

    #[cfg(not(target_os = "windows"))]
    {
        Err("Packaged BEKAL runtime initialization is currently supported on Windows only."
            .to_string())
    }
}

fn docker_executable() -> Result<PathBuf, String> {
    if Command::new("docker").arg("--version").output().is_ok() {
        return Ok(PathBuf::from("docker"));
    }

    #[cfg(target_os = "windows")]
    {
        if let Some(program_files) = env::var_os("ProgramFiles") {
            let candidate = PathBuf::from(program_files)
                .join("Docker")
                .join("Docker")
                .join("resources")
                .join("bin")
                .join("docker.exe");

            if candidate.is_file() {
                return Ok(candidate);
            }
        }
    }

    Err("Docker CLI is unavailable. Install Docker Desktop before running BEKAL.".to_string())
}

fn ensure_docker_available() -> Result<(), String> {
    let docker = docker_executable()?;
    let output = Command::new(&docker)
        .args(["info", "--format", "{{.ServerVersion}}"])
        .output()
        .map_err(|error| format!("Could not run Docker CLI: {error}"))?;

    if output.status.success() {
        return Ok(());
    }

    Err(format!(
        "Docker Desktop is installed but is not ready. Start Docker Desktop and reopen BEKAL. {}",
        output_message(&output)
    ))
}

fn running_services(runtime_root: &Path) -> Result<Vec<String>, String> {
    let output = compose(runtime_root, &["ps", "--status", "running", "--services"])?;

    if !output.status.success() {
        return Err(format!(
            "Could not inspect BEKAL services: {}",
            output_message(&output)
        ));
    }

    Ok(String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty())
        .map(ToOwned::to_owned)
        .collect())
}

fn run_migrations(runtime_root: &Path) -> Result<(), String> {
    let mut last_error = String::new();

    for _ in 0..15 {
        let output = compose(
            runtime_root,
            &["exec", "-T", "backend", "alembic", "upgrade", "head"],
        )?;

        if output.status.success() {
            return Ok(());
        }

        last_error = output_message(&output);
        thread::sleep(Duration::from_secs(1));
    }

    Err(format!("Database migration failed: {last_error}"))
}

fn wait_for_backend_health() -> Result<(), String> {
    for _ in 0..45 {
        if backend_is_healthy() {
            return Ok(());
        }

        thread::sleep(Duration::from_secs(2));
    }

    Err("BEKAL backend/database did not become healthy within 90 seconds.".to_string())
}

fn backend_is_healthy() -> bool {
    let address: SocketAddr = match "127.0.0.1:8000".parse() {
        Ok(address) => address,
        Err(_) => return false,
    };

    let mut stream = match TcpStream::connect_timeout(&address, Duration::from_millis(750)) {
        Ok(stream) => stream,
        Err(_) => return false,
    };

    let timeout = Some(Duration::from_secs(2));

    let _ = stream.set_read_timeout(timeout);
    let _ = stream.set_write_timeout(timeout);

    if stream
        .write_all(
            b"GET /api/health/db HTTP/1.1\r\n\
              Host: 127.0.0.1:8000\r\n\
              Connection: close\r\n\r\n",
        )
        .is_err()
    {
        return false;
    }

    let mut response = String::new();

    if stream.read_to_string(&mut response).is_err() {
        return false;
    }

    response.contains(" 200 ") && response.contains("\"status\":\"healthy\"")
}

fn checked_compose(runtime_root: &Path, arguments: &[&str], operation: &str) -> Result<(), String> {
    let output = compose(runtime_root, arguments)?;

    if output.status.success() {
        return Ok(());
    }

    Err(format!(
        "Unable to {operation}: {}",
        output_message(&output)
    ))
}

fn compose(runtime_root: &Path, arguments: &[&str]) -> Result<Output, String> {
    let docker = docker_executable()?;

    Command::new(docker)
        .current_dir(runtime_root)
        .arg("compose")
        .args(arguments)
        .output()
        .map_err(|error| format!("Could not execute Docker Compose: {error}"))
}

fn output_message(output: &Output) -> String {
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    format!("{stdout} {stderr}").trim().to_string()
}
