mod lifecycle;

use std::sync::{Arc, Mutex};

use lifecycle::LifecycleState;
use tauri::{Manager, RunEvent};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let lifecycle = Arc::new(Mutex::new(LifecycleState::default()));

    let setup_lifecycle = Arc::clone(&lifecycle);
    let shutdown_lifecycle = Arc::clone(&lifecycle);

    let app = tauri::Builder::default()
        .setup(move |app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let window = app
                .get_webview_window("main")
                .expect("BEKAL main window was not created");

            let startup_result = {
                let mut state = setup_lifecycle
                    .lock()
                    .unwrap_or_else(|poisoned| poisoned.into_inner());

                state.start(app.handle())
            };

            match startup_result {
                Ok(()) => {
                    // The hidden frontend may have loaded before
                    // FastAPI became healthy. Reload once so health
                    // state is always evaluated against ready services.
                    let _ = window.eval("window.location.reload()");

                    window.show()?;
                    window.set_focus()?;
                }

                Err(error) => {
                    log::error!("BEKAL service startup failed: {error}");

                    window.set_title("BEKAL - Startup failed")?;

                    window.show()?;
                    window.set_focus()?;
                }
            }

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building BEKAL");

    app.run(move |app_handle, event| {
        if let RunEvent::ExitRequested { api, .. } = event {
            let should_shutdown = {
                let mut state = shutdown_lifecycle
                    .lock()
                    .unwrap_or_else(|poisoned| poisoned.into_inner());

                state.begin_shutdown()
            };

            if should_shutdown {
                api.prevent_exit();

                {
                    let mut state = shutdown_lifecycle
                        .lock()
                        .unwrap_or_else(|poisoned| poisoned.into_inner());

                    state.shutdown();
                }

                app_handle.exit(0);
            }
        }
    });
}
