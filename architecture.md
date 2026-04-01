# Architecture Diagram (CI/CD)

```mermaid
graph TD
    classDef git fill:#24292e,stroke:#fff,color:#fff
    classDef action fill:#2088FF,stroke:#fff,color:#fff
    classDef hub fill:#0db7ed,stroke:#fff,color:#fff
    classDef docker fill:#2496ed,stroke:#fff,color:#fff
    classDef proxy fill:#009639,stroke:#fff,color:#fff
    classDef user fill:#f9a826,stroke:#fff,color:#000

    User((You)):::user -- "1. Push Code" --> GitHub[GitHub Repository]:::git
    GitHub -- "2. Triggers" --> Actions[GitHub Actions (CI)]:::action
    Actions -- "3. Build & Push Image" --> Hub[Docker Hub]:::hub
    
    subgraph Local Deployment (Windows Laptop)
        Watchtower[Watchtower (CD)]:::docker 
        Proxy[Nginx Reverse Proxy]:::proxy
        App[Flask Application]:::docker
        DB[(Expenses.json)]:::docker
        
        Hub -. "4. Checks every 30s" .-> Watchtower
        Watchtower -- "5. Pulls image & restarts container" --> App
        App <--> DB
        
        Client((Browser)):::user -- "HTTP :80" --> Proxy
        Proxy -- "Redirects to :8000" --> App
    end
```
