# Windows Installation

This guide covers the released **BEKAL v0.2.0 Windows desktop application**.

## Requirements

BEKAL V0.2 requires a Windows x64 PC and Docker Desktop installed and running. The released application already packages the BEKAL desktop UI and installed runtime template; normal users do not need to install Python, Node.js, Rust, Git, or Tesseract separately.

## Download

Use the official release page:

<https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0>

Download:

```text
BEKAL_0.2.0_x64-setup.exe
```

Expected SHA-256:

```text
E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```

## Verify the installer

In Windows PowerShell:

```powershell
Get-FileHash "$env:USERPROFILE\Downloads\BEKAL_0.2.0_x64-setup.exe" -Algorithm SHA256
```

The hash must match the value published above and on the GitHub release.

The current installer is unsigned. Windows SmartScreen may therefore display a publisher or reputation warning even when the file is genuine. Hash verification is the release-integrity check for V0.2.

## Install

Run `BEKAL_0.2.0_x64-setup.exe` and complete the installer normally.

V0.2 uses a per-user installation. The accepted owner-machine installation placed the executable under:

```text
%LOCALAPPDATA%\BEKAL\BEKAL.exe
```

A Start Menu shortcut is installed under the BEKAL folder.

## Launch

Start Docker Desktop first, then launch **BEKAL** from the Windows Start Menu.

On startup BEKAL prepares its private runtime if needed, starts its local PostgreSQL and FastAPI services, applies database migrations, waits for the database-backed health check, and shows the native BEKAL window only after the local runtime is ready.

The first launch can take longer than later launches because Docker may need to prepare the local backend runtime.

## Runtime and network behavior

The packaged runtime uses the Docker Compose project name `bekal-desktop`.

The backend is exposed only on:

```text
127.0.0.1:8000
```

PostgreSQL is not exposed on a host TCP port by the packaged runtime.

The installed private runtime is stored under:

```text
%LOCALAPPDATA%\com.haziqzes.bekal\runtime
```

It contains the generated private `.env`, managed runtime files, and private receipt storage. PostgreSQL data is kept in the stable Docker named volume used by the desktop Compose project.

## Normal shutdown

Close the BEKAL window normally with the window close button.

If BEKAL started its packaged services for that session, it stops those owned services on clean exit. Receipt PDFs, the generated private `.env`, and PostgreSQL data are preserved.

## Reinstall and upgrade behavior

V0.2 was owner-tested through install, save, close, relaunch, uninstall, reinstall, and data restoration.

The installer/runtime design preserves private data across a normal uninstall/reinstall cycle. Managed runtime files can be refreshed by a compatible application update while private data remains separate.

Before a future major-version upgrade, read that release's notes in case its data-migration policy changes.

## Uninstall

Use the normal Windows application uninstall flow.

The V0.2 uninstaller removes application binaries and shortcuts but intentionally preserves BEKAL private runtime data by default. This prevents an ordinary uninstall from silently deleting receipt history.

## Installing on another PC

Repeat the same Docker Desktop + BEKAL installer steps on the second Windows PC.

Each PC currently has its **own local BEKAL database and receipt storage**. V0.2 has no cloud sync, account system, or automatic PC-to-PC synchronization. Installing BEKAL on PC B does not import the receipt history from PC A.

## Smartphones

The Windows `.exe` installer cannot be installed on Android, iPhone, or iPad.

BEKAL V0.2 has no smartphone application. A future mobile experience would need a separate client and a secure networking/authentication design rather than trying to run the current Windows Docker/PostgreSQL desktop architecture directly on a phone.

## Troubleshooting

### BEKAL does not finish starting

Check that Docker Desktop is running and healthy. First startup can take several minutes while Docker prepares the backend.

### Port 8000 is already in use

The packaged backend expects `127.0.0.1:8000`. Stop the unrelated service using that port before starting BEKAL. Developers should also stop the repository development backend before testing the packaged application.

### SmartScreen warning

V0.2 is unsigned. Verify the installer SHA-256 against the release before running it.

### Receipt history is still present after uninstall

That is expected. V0.2 intentionally preserves private data across normal uninstall/reinstall.

### Another PC does not show my receipts

That is expected. Multi-device synchronization is not implemented.

## Release identity

```text
Release:    v0.2.0
Product:    BEKAL
Identifier: com.haziqzes.bekal
Installer:  BEKAL_0.2.0_x64-setup.exe
SHA-256:    E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```
