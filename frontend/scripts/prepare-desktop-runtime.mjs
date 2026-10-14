import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const scriptPath = fileURLToPath(import.meta.url)
const frontendRoot = path.resolve(path.dirname(scriptPath), '..')
const repoRoot = path.resolve(frontendRoot, '..')
const tauriRoot = path.join(frontendRoot, 'src-tauri')
const outputRoot = path.join(tauriRoot, 'generated-runtime')
const outputBackend = path.join(outputRoot, 'backend')

async function copyFile(source, destination) {
  await mkdir(path.dirname(destination), { recursive: true })
  await cp(source, destination, { force: true })
}

async function copyDirectory(source, destination) {
  await cp(source, destination, {
    recursive: true,
    force: true,
    filter: (entry) => {
      const basename = path.basename(entry)
      return basename !== '__pycache__' && basename !== '.pytest_cache'
    },
  })
}

await rm(outputRoot, { recursive: true, force: true })
await mkdir(outputBackend, { recursive: true })

await copyFile(
  path.join(repoRoot, 'desktop', 'docker-compose.yml'),
  path.join(outputRoot, 'docker-compose.yml'),
)

await copyFile(
  path.join(repoRoot, '.env.example'),
  path.join(outputRoot, '.env.example'),
)

await copyFile(
  path.join(repoRoot, 'backend', 'Dockerfile.desktop'),
  path.join(outputBackend, 'Dockerfile'),
)

for (const filename of ['pyproject.toml', 'alembic.ini']) {
  await copyFile(
    path.join(repoRoot, 'backend', filename),
    path.join(outputBackend, filename),
  )
}

for (const dirname of ['app', 'migrations']) {
  await copyDirectory(
    path.join(repoRoot, 'backend', dirname),
    path.join(outputBackend, dirname),
  )
}

const tauriConfig = JSON.parse(
  await readFile(path.join(tauriRoot, 'tauri.conf.json'), 'utf8'),
)

await writeFile(
  path.join(outputRoot, 'RUNTIME_VERSION'),
  `${tauriConfig.version}\n`,
  'utf8',
)

console.log(`Prepared BEKAL desktop runtime ${tauriConfig.version}`)
console.log(`Output: ${outputRoot}`)
