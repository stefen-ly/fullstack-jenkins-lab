# Jenkins Full-Stack CI/CD Lab — Spring Boot + ReactJS

A complete, small hands-on monorepo for **Git → Jenkinsfile → Docker builds/tests → optional deployment → Email + Telegram notifications**.

## Stack

- Spring Boot 4.1.2, Java 21, Maven, REST API (in-memory)
- React 19, Vite 7 (task board frontend)
- Docker Compose (build backend + frontend, local deploy)
- Jenkins Declarative Pipeline (`Jenkinsfile`)
- Jenkins Email Extension Plugin (SMTP must be configured)
- Jenkins Credentials Binding Plugin + Telegram Bot API (via Python 3)

## Folder layout

```text
fullstack-jenkins-lab/
├── Jenkinsfile
├── compose.yaml
├── backend/
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/java/... + src/test/java/...
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.js
│   └── src/App.jsx + src/taskHelpers.test.js
└── scripts/send_telegram.py
```

## 1. Test without Jenkins

Requirements: Docker Engine and `docker compose` on the same machine.

```bash
docker compose up --build -d
docker compose ps
curl -i http://127.0.0.1:8088/api/health
curl -i http://127.0.0.1:8088/api/tasks
```

Open **http://127.0.0.1:8088** **on the machine running Docker**. If this is an SSH VM, use SSH/VS Code port forwarding: local port `8088` → VM port `8088`, or open browser inside VM. Compose binds to host loopback by default.

API:
- `GET /api/health`
- `GET /api/tasks`
- `POST /api/tasks` with `{"title":"Learn Jenkins"}`
- `PATCH /api/tasks/{id}/toggle`
- `DELETE /api/tasks/{id}`

The backend uses **in-memory data** and resets on restarts.

Stop containers:

```bash
docker compose down
```

## 2. Git/GitHub setup

Unzip, then run in the **project root**:

```bash
git init -b main
git add .
git commit -m "Initial fullstack Jenkins lab"
# Create an empty GitHub repository called fullstack-jenkins-lab first
git remote add origin https://github.com/YOUR_USERNAME/fullstack-jenkins-lab.git
git push -u origin main
```

For reproducible frontend dependencies, recommended before committing: `cd frontend && npm install && cd ..`. This creates `frontend/package-lock.json`, which should be committed; then frontend Docker build uses `npm ci`. The starter ZIP does **not** contain a lockfile because npm registry access was not available when packaging. Without lockfile the Dockerfile uses `npm install` for the first build.

## 3. Jenkins prerequisites

- An existing Jenkins Controller and a **dedicated trusted** build Agent labeled `docker-ready`.
- Docker Engine, Docker Compose v2, Git, Python 3 and curl installed on that Agent.
- Jenkins Job must be authorized to invoke Docker on that Agent. **Warning:** Docker daemon access gives powerful host privileges; do not grant it to untrusted pipelines or use the Controller as a general build machine.
- Jenkins Plugins: **Pipeline**, **Git**, **Email Extension**, **Credentials Binding**. Check availability under Manage Jenkins → Plugins.
- SMTP already configured/tested: Manage Jenkins → System → Extended E-mail Notification (e.g. SMTP host/port, authentication, TLS).
- Telegram Bot: create with BotFather, start a chat with it, obtain bot token + correct chat ID.

Add two Jenkins Credentials under **Manage Jenkins → Credentials** (kind **Secret text**):
- ID `telegram-bot-token`: actual bot token
- ID `telegram-chat-id`: destination chat ID

Never commit the token, Chat ID, SMTP password or Jenkins credentials to Git.

## 4. Create Jenkins Pipeline from Git

1. Jenkins → **New Item** → Pipeline → name `fullstack-jenkins-lab`.
2. Pipeline **Definition**: `Pipeline script from SCM`.
3. SCM: **Git**, URL: `https://github.com/YOUR_USERNAME/fullstack-jenkins-lab.git`.
4. Branch Specifier: `*/main`; Script Path: `Jenkinsfile`.
5. For a private repo set a Git read credential in the SCM config.
6. Save. Click **Build Now** once; Jenkins evaluates `parameters {}` and thereafter exposes **Build with Parameters**. Initial run may have blank default parameters; it will still build.

Parameters:
- `EMAIL_TO`: your destination email (required to send email; blank skips email).
- `DEPLOY_LOCAL`: defaults **false**. Set true to deploy on the agent host at 127.0.0.1:8088.
- `SIMULATE_FAILURE`: defaults **false**. Set true for an intentional failure after build/test.

Pipeline uses `checkout scm`; it is designed for **Pipeline script from SCM**, not a standalone pasted UI script without SCM configuration.

## 5. Test success and failure notifications

**SUCCESS:** EMAIL_TO=you@example.com, DEPLOY_LOCAL=true, SIMULATE_FAILURE=false. Expect Docker build (backend Maven test; frontend Node tests + Vite build), deploy, API curl smoke check, artifact `ci-summary.txt`, email, Telegram.

**FAILURE:** EMAIL_TO=you@example.com, SIMULATE_FAILURE=true. Tests/build run, then pipeline deliberately fails, `post { always {} }` sends status FAILURE to both channels; deploy stage is skipped.

Notification failures are handled so they don't overwrite the original pipeline result. If SMTP or credentials are misconfigured, read the Console Output warnings.

**Git push trigger:** Start with manual `Build with Parameters`. Later configure Jenkins GitHub integration and a webhook pointing to **a reachable Jenkins HTTPS address**, normally `https://YOUR_JENKINS_HOST/github-webhook/` if using GitHub integration plugin. `localhost` URL from your laptop cannot be reached by GitHub; alternatively use Poll SCM in labs. Never expose an unsecured Jenkins controller on the public Internet.

## 6. Smoke test manually

```bash
curl -i http://127.0.0.1:8088/api/health
curl -i http://127.0.0.1:8088/api/tasks
curl -i -X POST http://127.0.0.1:8088/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"CI/CD lab complete"}'
```

## 7. Local dev (optional, without Docker)

Requires Java 21, Maven 3.6.3+, Node >=20.19 (Node 24 recommended):

Terminal A:
```bash
cd backend
mvn spring-boot:run
```

Terminal B:
```bash
cd frontend
npm install
npm test
npm run dev
```

Browser http://localhost:5173; Vite proxies `/api` to Spring Boot on localhost:8080.

## Caveats

- **In-memory database:** data does not survive backend restarts; this is intentional for a small CI/CD teaching lab.
- **No real deployments on Git push by default:** `DEPLOY_LOCAL=false` avoids unexpectedly overwriting apps running on the agent host.
- **Agent localhost vs your laptop:** deployment opens port 8088 on the agent host loopback, use port forwarding if remote.
- **No integration secrets in Git:** only credential IDs are present.
- **No automatic notifications if the post block cannot start:** e.g. Jenkins Controller process unavailable or the Job never started.
- **Do not run untrusted PR code on a Docker-privileged agent.**
