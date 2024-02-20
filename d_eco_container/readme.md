# Authentication with GitHub Container Registry
Before building your Docker image, ensure you're authenticated with GHCR to allow pulling private images. Use the 
docker login command with your GitHub username and a Personal Access Token (PAT) that has the appropriate scopes 
(read:packages at a minimum).

```bash
echo "YOUR_PERSONAL_ACCESS_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```



