# Sistem-de-monitorizare-automata-a-traficului-de-retea-cod-sursa-si-configuratii
# Automatizarea procesului de monitorizare a traficului de date într-o rețea de calculatoare

## Despre proiect

Acest proiect implementează un sistem complet și funcțional de monitorizare automată a traficului de date dintr-o rețea de calculatoare, construit **exclusiv din componente open-source**, fără a depinde de echipamente fizice costisitoare sau de licențe comerciale.

Sistemul colectează periodic statistici de la routere prin protocolul **NETCONF**, le procesează pentru a calcula rate de trafic în timp real, le stochează într-o bază de date de tip serie temporală și le vizualizează prin panouri interactive, cu alertare automată la detectarea anomaliilor de trafic.

Lucrarea demonstrează că un sistem profesional de monitorizare poate fi construit integral cu instrumente gratuite, oferind o alternativă viabilă, flexibilă și accesibilă față de soluțiile comerciale existente.



## Arhitectura sistemului

Sistemul este organizat sub forma unui flux de date în patru etape:

GNS3 (emulare)  →  NETCONF (colectare)  →  Python (procesare)  →  InfluxDB (stocare)  →  Grafana (vizualizare)

1. **Emulare** – topologia de rețea este emulată în GNS3, folosind imagini oficiale Cisco IOS-XE rulate prin QEMU/KVM, astfel încât comportamentul routerelor virtuale să fie apropiat de cel al echipamentelor fizice.
2. **Colectare** – un script Python stabilește sesiuni NETCONF periodice cu fiecare router și extrage statisticile de interfață în format XML, conform modelului YANG `ietf-interfaces`.
3. **Procesare** – contoarele cumulative de octeți sunt transformate în rate instantanee de trafic, exprimate în biți pe secundă.
4. **Stocare** – datele sunt persistate în InfluxDB, o bază de date optimizată pentru serii temporale.
5. **Vizualizare** – Grafana afișează datele în timp real și declanșează alerte automate prin email la depășirea pragurilor configurate.

---

## Tehnologii utilizate

| Componentă | Tehnologie | Rol |
|---|---|---|
| Emulare rețea | GNS3 (QEMU/KVM) | Rularea topologiei cu routere Cisco CSR1000v |
| Protocol management | NETCONF (peste SSH) | Colectarea structurată a datelor |
| Modelare date | YANG (`ietf-interfaces`) | Definirea structurii datelor colectate |
| Limbaj programare | Python | Scriptul de colectare și procesare |
| Biblioteci Python | ncclient, xmltodict, influxdb | Comunicare NETCONF, parsare XML, scriere în baza de date |
| Bază de date | InfluxDB | Stocarea seriilor temporale |
| Vizualizare | Grafana | Dashboard-uri și alertare automată |
  

## Funcționalități

- Colectarea automată a statisticilor de interfață la interval de **10 secunde**
- Calcularea ratelor de trafic în timp real (biți pe secundă)
- Stocarea persistentă a datelor în InfluxDB
- Vizualizarea traficului în dashboard-uri Grafana, per dispozitiv și per interfață
- Alertare automată prin email la depășirea pragurilor configurate
- **Toleranță la erori**: colectarea continuă chiar dacă un router devine temporar indisponibil, reluând automat la revenirea acestuia


## Validare

Funcționalitatea sistemului a fost validată printr-un scenariu de testare realist, care simulează un atac cibernetic de tip **DoS (Denial of Service)** asupra interfeței principale a routerului central. Rezultatele au confirmat:

- detectarea anomaliei în maximum **10 secunde** de la inițierea atacului;
- declanșarea automată a alertei prin email, fără intervenție umană;
- continuitatea colectării datelor pe durata incidentului;
- persistența datelor fără pierderi în cazul reporniri scriptului.

Comparativ cu soluțiile clasice bazate pe SNMP (interval de interogare de 5 minute), sistemul implementat oferă o îmbunătățire de aproximativ **30 de ori** a timpului de detectare.






## Licență

Acest proiect este disponibil sub licența MIT.
