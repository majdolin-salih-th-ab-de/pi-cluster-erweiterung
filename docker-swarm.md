# Docker Swarm Setup

[Docker Docs](https://docs.docker.com/engine/swarm/)

Für einen echten „Produktiv-Einsatz“ über mehrere physische Hosts kannst du Docker Swarm nutzen. Die Schritte sind grob:

1. **Docker Swarm initialisieren**  
   - Auf **einem** Pi (dem Manager) ausführst du:
     ```bash
     docker swarm init --advertise-addr <IP-des-Manager-Pi>
     ```
   - Du bekommst dann einen „Join Token“ angezeigt.

2. **Worker-Nodes beitreten lassen**  
   - Auf **jedem** Worker-Pi führst du den Befehl aus, den Swarm beim `init` ausgespuckt hat, z.B.:
     ```bash
     docker swarm join --token SWMTKN-1-xyz... <IP-des-Manager-Pi>:2377
     ```
   - Danach sind alle Worker-Pis Teil deines Swarms.

3. **Ein Docker-Stack-File** (`docker-stack.yml`) definieren  
   - Anstelle von `docker-compose` direkt nutzt man bei Swarm sogenannte Stacks. Du kannst ein `version: "3.8"` (o.ä.) Compose-File nehmen, das so aussieht:
     ```yaml
     version: "3.8"
     services:
       main:
         image: pi_cluster:latest
         ports:
           - "5001:5001"
         environment:
           - TOTAL_SAMPLES=3000000
           - EXPECTED_WORKERS=4
         networks:
           - pi_net
         deploy:
           replicas: 1   # nur 1 main
           placement:
             constraints: [node.role == manager]  # z.B. nur auf dem Manager laufen

       worker:
         image: pi_cluster:latest
         environment:
           - MAIN_HOST=main
           - MAIN_PORT=5001
         networks:
           - pi_net
         deploy:
           replicas: 3   # Anzahl Worker
     networks:
       pi_net:
         driver: overlay
     ```
   - Hier nutzen wir ein **Overlay-Netzwerk** `driver: overlay`, das unter Swarm bei allen Knoten existiert.

4. **Stack ausrollen**  
   - Auf dem Manager-Pi machst du:
     ```bash
     docker stack deploy -c docker-stack.yml pi_cluster
     ```
   - Docker Swarm erstellt jetzt den Service `main` (1 Replica) auf dem Manager und den Service `worker` (3 Replicas) verteilt auf die Worker-Knoten.  
   - Durch das Overlay-Netzwerk können sich `main` und `worker` per Service-Namen (`main`) erreichen.  

5. **Prüfen**  
   - `docker service ls` zeigt die Services an,  
   - `docker service ps pi_cluster_main` bzw. `docker service ps pi_cluster_worker` zeigt, auf welchen Hosts die Tasks laufen.

---

### Fazit zu Swarm
- **Vorteil**: sehr einfache Skalierung („3 Worker-> 10 Worker“ mit einem Befehl).  
- **Nachteil**: Du musst dir die Swarm-Architektur (Manager/Worker) und das Overlay-Netzwerk einrichten. Zudem hat Docker Swarm (verglichen mit Kubernetes) geringeren Fokus in der Community, ist aber nach wie vor sehr kompakt und schnell konfiguriert.

---

## Zusammenfassung
- Mit den beiden separaten Compose-Files (`docker-compose.main.yml` und `docker-compose.worker.yml`) kannst du **ohne** Swarm sehr einfach dein verteiltes Setup testen – pro Pi ein „`docker-compose up -d`“.  
- Für „professionellere“ oder automatisierte Deployments auf mehreren Hosts ist Docker Swarm (oder Kubernetes) empfehlenswert, erfordert aber ein zusätzliches Initialisieren des Clusters und den Einsatz von Overlay-Netzwerken.  