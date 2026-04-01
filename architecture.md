# Diagramme d'Architecture (CI/CD)

```mermaid
graph TD
    classDef git fill:#24292e,stroke:#fff,color:#fff
    classDef action fill:#2088FF,stroke:#fff,color:#fff
    classDef hub fill:#0db7ed,stroke:#fff,color:#fff
    classDef docker fill:#2496ed,stroke:#fff,color:#fff
    classDef proxy fill:#009639,stroke:#fff,color:#fff
    classDef user fill:#f9a826,stroke:#fff,color:#000

    User((Vous)):::user -- "1. Push Code" --> GitHub[Dépôt GitHub]:::git
    GitHub -- "2. Déclenche" --> Actions[GitHub Actions (CI)]:::action
    Actions -- "3. Build & Push Image" --> Hub[Docker Hub]:::hub
    
    subgraph Déploiement Local (Laptop Windows)
        Watchtower[Watchtower (CD)]:::docker 
        Proxy[Nginx Reverse Proxy]:::proxy
        App[Application Flask]:::docker
        DB[(Expenses.json)]:::docker
        
        Hub -. "4. Vérifie chaque 30s" .-> Watchtower
        Watchtower -- "5. Pull image & redémarre conteneur" --> App
        App <--> DB
        
        Client((Navigateur)):::user -- "HTTP :80" --> Proxy
        Proxy -- "Redirige vers :8000" --> App
    end
```
