# Security Policy

## Supported version

The currently supported public release is:

| Version | Supported |
| --- | --- |
| 0.2.x | Yes |
| 0.1.x | Historical |

Security fixes may be released as maintenance updates when appropriate.

## Security model

BEKAL V0.2 is designed as a local-first, single-user Windows application.

The supported packaged topology keeps:

- FastAPI on loopback (`127.0.0.1:8000`);
- PostgreSQL unexposed to a host TCP port;
- receipt PDFs and generated environment data in private local runtime storage;
- real household data outside the public source repository.

BEKAL V0.2 does not claim to be a supported remote multi-user service. Exposing the current unauthenticated backend to a LAN or the public internet is outside the supported security model.

## Reporting a vulnerability

Please do **not** include sensitive user data in a public issue.

In particular, never attach:

- real receipts;
- private CSV exports;
- database dumps containing household data;
- credentials, passwords, API keys, or access tokens;
- private `.env` files;
- private application logs containing receipt content.

If GitHub private vulnerability reporting is available for this repository, use that private reporting channel.

If a private reporting channel is not available, open a minimal public issue that states a security-sensitive problem needs a private discussion **without including exploit details, credentials, or user data**.

Useful information to provide privately includes:

- affected BEKAL version;
- operating system/environment;
- affected component;
- minimal reproduction steps using synthetic data;
- expected vs actual behavior;
- impact assessment;
- suggested mitigation if known.

## Installer verification

The official BEKAL v0.2.0 Windows installer is currently unsigned.

Verify the release SHA-256 before running it:

```text
BEKAL_0.2.0_x64-setup.exe
E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```

Official release:

<https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0>

An unsigned-publisher SmartScreen/reputation warning by itself is a known V0.2 distribution limitation, not evidence that a correctly hashed installer has been modified.

## Repository privacy defects

Treat any accidental inclusion of real receipt data, secrets, credentials, or private runtime files in reachable Git history as a security/privacy incident.

The repository includes an automated safety/history scanner. Privacy gates must not be bypassed to make CI pass.

## Dependency advisories

Dependency advisories are reviewed as maintenance work. A remediation should use the smallest safe change that resolves the affected path while preserving BEKAL's tested runtime behavior.

Do not publicly paste sensitive local configuration when reporting a dependency/security problem.

## Scope notes

The following are outside the supported V0.2 security model and require separate design review before they are considered supported:

- remote internet exposure;
- household accounts/authentication;
- multi-user access;
- mobile clients connecting remotely;
- cloud synchronization;
- public hosted BEKAL instances.

See [Privacy & Security](docs/privacy-security.md) for the full data boundary.
