use std::{
    env,
    io::{Read, Write},
    net::{SocketAddr, TcpStream},
    path::{Path, PathBuf},
    process::{Command, Output},
    thread,
    time::Duration,
};

#[derive(Default)]
pub struct LifecycleState {
    repo_root: Option<PathBuf>,
    owns_services: bool,
    shutdown_started: bool,
}

impl LifecycleState {
    pub fn start(&mut self) -> Result<(), String> {
        let repo_root = find_repo_root()?;

        ensure_docker_available()?;

        let running_before = running_services(&repo_root)?;

        let shared_session = running_before
            .iter()
            .any(|service| matches!(service.as_str(), "postgres" | "backend" | "frontend"));

        self.repo_root = Some(repo_root.clone());
        self.owns_services = !shared_session;

        let startup_result = (|| {
            checked_compose(
                &repo_root,
                &["up", "-d", "postgres", "backend"],
                "start PostgreSQL and backend",
            )?;

            run_migrations(&repo_root)?;

            wait_for_backend_health()?;

            Ok(())
        })();

        if let Err(error) = startup_result {
            if self.owns_services {
                let _ = compose(&repo_root, &["stop", "backend", "postgres"]);
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

        if let Some(repo_root) = self.repo_root.as_ref() {
            let _ = compose(repo_root, &["stop", "backend", "postgres"]);
        }

        self.owns_services = false;
    }
}

fn find_repo_root() -> Result<PathBuf, String> {
    if let Some(explicit_root) = env::var_os("BEKAL_REPO_ROOT") {
        let path = PathBuf::from(explicit_root);

        if is_repo_root(&path) {
            return Ok(path);
        }

        return Err("BEKAL_REPO_ROOT does not contain docker-compose.yml and .env.".to_string());
    }

    if let Ok(current_dir) = env::current_dir() {
        if let Some(root) = search_ancestors(&current_dir) {
            return Ok(root);
        }
    }

    if let Ok(executable) = env::current_exe() {
        if let Some(parent) = executable.parent() {
            if let Some(root) = search_ancestors(parent) {
                return Ok(root);
            }
        }
    }

    Err("Could not locate the Project-BEKAL repository. \
         Set BEKAL_REPO_ROOT to the repository directory."
        .to_string())
}

fn search_ancestors(start: &Path) -> Option<PathBuf> {
    for ancestor in start.ancestors() {
        if is_repo_root(ancestor) {
            return Some(ancestor.to_path_buf());
        }
    }

    None
}

fn is_repo_root(path: &Path) -> bool {
    path.join("docker-compose.yml").is_file()
        && path.join(".env").is_file()
        && path.join("backend").is_dir()
        && path.join("frontend").is_dir()
}

fn ensure_docker_available() -> Result<(), String> {
    let output = Command::new("docker")
        .args(["info", "--format", "{{.ServerVersion}}"])
        .output()
        .map_err(|error| format!("Docker command is unavailable: {error}"))?;

    if output.status.success() {
        return Ok(());
    }

    Err(format!(
        "Docker Desktop is not ready: {}",
        output_message(&output)
    ))
}

fn running_services(repo_root: &Path) -> Result<Vec<String>, String> {
    let output = compose(repo_root, &["ps", "--status", "running", "--services"])?;

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

fn run_migrations(repo_root: &Path) -> Result<(), String> {
    let mut last_error = String::new();

    for _ in 0..15 {
        let output = compose(
            repo_root,
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

fn checked_compose(repo_root: &Path, arguments: &[&str], operation: &str) -> Result<(), String> {
    let output = compose(repo_root, arguments)?;

    if output.status.success() {
        return Ok(());
    }

    Err(format!(
        "Unable to {operation}: {}",
        output_message(&output)
    ))
}

fn compose(repo_root: &Path, arguments: &[&str]) -> Result<Output, String> {
    Command::new("docker")
        .current_dir(repo_root)
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
