# 13 Dependencies and Costs — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`

---

## External Services and API Providers

| Service | Purpose | Tier | Cost Model | Notes |
|---------|---------|------|------------|-------|
| Roboflow | Dataset download (4 projects) | Free/Paid | Free tier available; paid for private workspaces/higher quotas | API key required; versions unpinned |
| Kaggle | GPU T4 x2 training | Free | ~30 GPU hours/week per account; sessions up to 12 hours | Phone verification required; internet must be enabled |
| ntfy.sh | Training notifications | Free | Free; self-hosting optional | Optional; topic name via Kaggle Secret |
| GitHub | Code repository; CI/CD | Free | Free for public repositories | Actions minutes free for public repos |
| Expo | Mobile build service | Free/Paid | Free tier available; EAS Build has usage limits | Android APK/AAB builds |

---

## Hosting Options (Backend — Not Yet Selected)

No hosting provider has been selected. Options to evaluate:

| Option | Estimated Cost | Suitability | Notes |
|--------|---------------|-------------|-------|
| Railway | ~$5-20/month | Good for small backend | Simple deployment; GPU options available |
| Render | ~$7-25/month | Good for small backend | Free tier available; GPU not on free tier |
| Fly.io | ~$2-20/month | Good for small backend | GPU options available |
| AWS EC2 (g4dn.xlarge, T4 GPU) | ~$0.526/hour (~$380/month) | Overkill for MVP | GPU for inference; probably unnecessary |
| AWS Lambda | Pay per request | Risky for model | Cold starts; runtime limits; not tested |
| Google Cloud Run | Pay per request | Risky for model | Container limits; GPU not available |
| Hetzner Cloud | ~$5-40/month | Good value | GPU options available |

**Recommendation:** Start with a simple CPU-based backend (Railway/Render/Fly.io) at ~$5-20/month. Measure inference latency and memory before considering GPU. Do not assume serverless can run the model efficiently without testing cold starts.

---

## Database Options (Deferred to Later Phase)

| Option | Estimated Cost | Notes |
|--------|---------------|-------|
| Supabase (free tier) | $0/month | 500 MB database; suitable for MVP history |
| Supabase (paid) | ~$25/month | More storage; higher limits |
| Self-hosted PostgreSQL | ~$5-20/month (VPS) | More control; more ops overhead |

**Not required for MVP.** Add only when history/accounts/cloud persistence approved.

---

## Development Dependencies

### ai-model/ (Training Pipeline)

| Package | Version Specifier | Purpose | Cost |
|---------|------------------|---------|------|
| ultralytics | ~=8.4.212 | YOLO training/inference | Free (open source) |
| roboflow | ~=1.7.3 | Dataset download | Free (API key required) |
| pyyaml | ~=6.0.3 | YAML config parsing | Free (open source) |
| pillow | ~=12.3.0 | Image processing | Free (open source) |
| pytest | ~=9.1.1 | Testing (dev) | Free (open source) |

### backend/ (Inference API)

| Package | Version Specifier | Purpose | Cost |
|---------|------------------|---------|------|
| fastapi | — | Web framework | Free (open source) |
| uvicorn | — | ASGI server | Free (open source) |
| pydantic | — | Data validation | Free (open source) |
| pillow / opencv-python | — | Image processing | Free (open source) |
| onnxruntime | — | ONNX inference | Free (open source) |
| torch | — | PyTorch (if not using ONNX) | Free (open source) |
| ultralytics | — | YOLO model loading | Free (open source) |

### mobile/ (React Native + Expo)

| Package | Purpose | Cost |
|---------|---------|------|
| expo | Framework | Free (open source) |
| react-native | UI framework | Free (open source) |
| expo-camera | Camera access | Free (open source) |
| expo-image-picker | Gallery access | Free (open source) |
| zustand | State management | Free (open source) |
| expo-router | Navigation | Free (open source) |

---

## Estimated Monthly Operating Costs (MVP)

| Component | Low Estimate | High Estimate | Notes |
|-----------|-------------|---------------|-------|
| Backend hosting (CPU) | $5/month | $25/month | Depends on provider and instance size |
| Domain name | $1/month | $2/month | ~$12-24/year |
| SSL certificate | $0/month | $0/month | Let's Encrypt (free) |
| Database (Supabase free) | $0/month | $0/month | Not needed for MVP |
| Model storage | $0/month | $0/month | Git LFS or release assets (free tier) |
| Monitoring (basic) | $0/month | $10/month | Free tiers available |
| **Total (MVP)** | **~$6/month** | **~$37/month** | Excludes development time |

---

## Estimated Costs at Scale (Post-MVP)

| Component | Low Estimate | High Estimate | Notes |
|-----------|-------------|---------------|-------|
| Backend hosting (GPU) | $100/month | $500/month | GPU instance for inference |
| Database (Supabase paid) | $25/month | $100/month | With auth and history |
| Monitoring (paid) | $20/month | $100/month | Full APM |
| Bandwidth | $10/month | $100/month | Depends on usage |
| **Total (scaled)** | **~$155/month** | **~$800/month** | Highly variable |

---

## Free vs Paid Distinction

| Item | Free Tier | Paid Required When |
|------|-----------|-------------------|
| GitHub repository | Unlimited public repos | Private repos (if needed) |
| GitHub Actions | 2,000 minutes/month (public repos) | More minutes; private repos |
| Kaggle GPU | ~30 hours/week | More hours (paid) |
| Roboflow | Public datasets; limited private | Private workspaces; higher quotas |
| Expo/EAS | Free builds with limits | More builds; larger binaries |
| Supabase | 500 MB database | More storage; higher limits |
| Let's Encrypt SSL | Free | Never (always free) |
| ntfy.sh | Free | Self-hosting (optional) |

---

## Cost Risks

1. **Kaggle GPU hours:** ~30 hours/week per account. One training run takes 8-9 hours. Multiple runs could exhaust the weekly quota.
2. **Model storage:** Weights not in Git. Need external storage (Git LFS, release assets, or cloud storage).
3. **Backend inference:** CPU inference at ~70ms/image on 2-core CPU. Concurrent users will need multiple instances or GPU.
4. **Mobile builds:** EAS Build has usage limits on free tier.

---

## Recommended Initial Stack (MVP)

| Component | Choice | Estimated Cost |
|-----------|--------|----------------|
| Code repository | GitHub (public) | $0 |
| CI/CD | GitHub Actions | $0 |
| Training | Kaggle GPU T4 x2 | $0 (within 30h/week) |
| Model storage | GitHub releases or Git LFS | $0 |
| Backend hosting | Railway/Render/Fly.io (CPU) | $5-20/month |
| Domain | Namecheap/Cloudflare | ~$1/month |
| SSL | Let's Encrypt | $0 |
| Mobile builds | EAS Build | $0 (within free limits) |
| **Total monthly** | | **~$6-21/month** |
