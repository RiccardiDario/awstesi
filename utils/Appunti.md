# Guida all'uso di Ansible, Terraform e AWS CLI in ambiente WSL

Questa guida contiene tutte le istruzioni necessarie per configurare e utilizzare **Ansible**, **Terraform** e **AWS CLI** in ambiente **WSL** (Windows Subsystem for Linux). È utile per chi desidera automatizzare il provisioning e il deploy di applicazioni su AWS partendo da un sistema Windows.

---

## Installazione di Ansible

Ansible non è compatibile direttamente con Windows. Per questo motivo, si consiglia una delle seguenti soluzioni:

- Utilizzare **WSL** (Windows Subsystem for Linux)
- Utilizzare una **macchina virtuale** con una distribuzione Linux
- Utilizzare un **container** con una distribuzione Linux

Se scegli WSL, ricorda che **l'intero progetto deve essere salvato all'interno del file system WSL**. Progetti salvati su Windows e accessibili da WSL **non funzionano correttamente**. Visual Studio Code permette di lavorare direttamente all’interno di WSL utilizzando l’estensione Remote Explorer. Per installare Ansible su WSL, esegui:

```bash
sudo apt update && sudo apt install -y ansible
```

### Modifica dei permessi sulla chiave AWS

Per far sì che Ansible possa usare correttamente la chiave `.pem`, è necessario modificarne i permessi:

```bash
chmod 600 nomechiave.pem
```

> ⚠️ Nota: Ansible si basa su Python per poter funzionare correttamente. Se una macchina AWS non ha Python installato, Ansible potrebbe non riuscire a operare. In questi casi, ci sono due possibilità: installare Python manualmente sulla macchina prima di utilizzare Ansible, oppure installarlo direttamente tramite Ansible, ma con alcune accortezze. Infatti, Ansible esegue di default il modulo gather_facts all'inizio di ogni playbook, il cui scopo è raccogliere informazioni sul sistema. Questo modulo, però, richiede Python per funzionare. Se Python non è presente, gather_facts fallirà e l’intero playbook si interromperà. Per evitare questo problema, bisogna disabilitare temporaneamente gather_facts, utilizzare la direttiva raw (che consente di eseguire comandi SSH senza dipendere da Python) per installare Python, e solo dopo riattivare gather_facts. A quel punto si potrà proseguire con l'esecuzione normale dello script Ansible.

---

## Installazione di `rsync`

`rsync` è uno strumento utile per copiare e sincronizzare file, sia in locale che tra host remoti. È spesso usato per backup o deploy. In questo progetto, viene utilizzato per copiare l’intero contenuto del progetto WebAppPostQuantumServer — comprese tutte le sottocartelle — sulla macchina AWS tramite un semplice script.
Installalo sia sulla tua macchina (WSL) che su AWS:

```bash
sudo apt install rsync -y
```

---

## Utilizzo di Ansible

### Per il server:

```bash
ansible-playbook -i inventoryserver.ini install_env.yml
ansible-playbook -i inventoryserver.ini deploy_server.yml
```
>All'interno del file inventoryserver.ini sono specificati indirizzi IP e percorsi delle chiavi, che possono variare da un progetto all’altro. Prima di utilizzarlo, è importante verificare che le informazioni inserite siano corrette. Inoltre, se la macchina utilizza un IP elastico anziché un IP statico, quest’ultimo potrebbe cambiare ogni volta che la macchina viene riavviata. Con terraform è possibile generare questo file in maniera automatica con lo script python inventory_generator.py

---

## Installazione di Terraform su WSL
>Attenzione Terraform è disponibile anche per Windows. Si è scelto di utilizzarlo in WSL per evitare di avere delle incompatibilità con Ansible

### Passaggi:

1. Aggiorna i pacchetti e installa le dipendenze:

```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
```

2. Aggiungi la chiave GPG di HashiCorp:

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
```

3. Aggiungi il repository ufficiale:

```bash
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

4. Installa Terraform:

```bash
sudo apt-get update && sudo apt-get install terraform
```

5. Verifica l'installazione:

```bash
terraform -v
```
>Prima di poter utilizzare terraform bisgona ricavare le credenziali dell'acccount aws. Per far ciò ci sono vari metodi. Qui viene presentato quello con AWS CLI
---

## Installazione e configurazione di AWS CLI

Verifica se AWS CLI è già installato nella WSL
```bash
aws --version
```
Se non è installato, procedi con i seguenti comandi:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install unzip curl -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
Pulizia dei file di installazione:
>I file generati da questa installazione possono essere rimosssi completamente dal progetto


Ora la verifica dovrebbe andare a buon fine:
```bash
aws --version
```

Se è tutto corretto, configura le credenziali:

```bash
aws configure
```

Dovrai inserire:

- **AWS Access Key ID**: fornita dal tuo utente IAM su AWS
- **AWS Secret Access Key**: associata alla chiave sopra
- **Default region**: ad esempio `eu-north-1`
- **Default output format**: `json`

Queste credenziali devono essere ricavate dalla console di AWS:
### 🔐 Come ottenere le credenziali AWS (Access Key ID e Secret Access Key)

Per ottenere le credenziali necessarie alla configurazione della AWS CLI:

1. Accedi alla [console di gestione AWS](https://console.aws.amazon.com/)
2. Vai alla sezione **IAM** (puoi cercarla nella barra di ricerca in alto)
3. Nel menu laterale sinistro, clicca su **Users (Utenti)**
4. Seleziona l’utente per il quale vuoi generare le credenziali (oppure creane uno nuovo)
5. Vai nella scheda **Security credentials (Credenziali di sicurezza)**
6. Scorri fino a **Access keys** e clicca su **Create access key**
7. Seleziona l'uso "altro", poi **Next**
8. Conferma e copia:
   - **AWS Access Key ID**
   - **AWS Secret Access Key**

> ⚠️ Salva la Secret Access Key in un posto sicuro! Dopo la creazione non potrai più visualizzarla.
### 🔐 Quali permessi servono all’utente IAM per usare Terraform

#### ✅ Opzione consigliata per iniziare (ambiente di test)

Assegna all’utente la policy gestita di AWS:

```text
AdministratorAccess
```

Questa policy fornisce pieno accesso a tutte le risorse AWS, utile per testare Terraform senza problemi di permessi.

---

#### 🔒 Opzione più sicura (ambiente di produzione)

Crea una **policy personalizzata** che includa solo i permessi strettamente necessari. Puoi adattare la policy in base ai servizi AWS usati nei tuoi progetti Terraform (es. `rds:*`, `lambda:*`, `ecr:*`, `route53:*`, ecc.).

---

#### 📌 Come assegnare la policy all’utente IAM

1. Vai in **IAM > Users > [nome utente] > Add permissions**
2. Seleziona **Attach policies directly**
3. Cerca e seleziona:  
   ✅ `AdministratorAccess` (oppure la tua policy personalizzata)
4. Clicca su **Next** e poi **Add permissions**
---

Per verificare che le credenziali siano state configurate correttamente:
```bash
aws sts get-caller-identity
```
Questo comando restituisce l’ARN dell’utente, confermando che l’autenticazione è andata a buon fine.

---

## Uso di Terraform per creare un'istanza EC2

Vai nella cartella del progetto:

```bash
cd terraform
terraform init
```

Opzionale: verifica che `main.tf` sia scritto correttamente:

```bash
terraform plan
```

Applica la configurazione per generare l’istanza:

```bash
terraform apply
```

---

Per eliminare l'istanza della macchina con tutte le relative risorse:
>Attenzione: non eliminare i file generati durante tutto il processo. Questi file contengono lo stato di Terraform relativo alla macchina e alle risorse associate. Lo stato viene salvato solo localmente sul computer che esegue Terraform. Se questi file non sono presenti, il comando di distruzione delle risorse non funzionerà correttamente.
```bash
terraform destroy
```

>Anche se l'istanza risulta elimita sarà ancora presente nella console di AWS. Ci vogliono un paio di ore affinché AWS la cancelli definitivamente dai suoi sistemi. 
---

## Come trovare l’AMI più aggiornata di Ubuntu

All'interno del file main.tf è necessario specificare l'AMI dell'istanza voluta. Il seguente comando restituisce l'id dell’ultima immagine ufficiale Ubuntu:

```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
           "Name=state,Values=available" \
  --region eu-north-1 \
  --query 'Images[*].[ImageId,CreationDate]' \
  --output text | sort -k2 -r | head -n1 | awk '{print $1}'

```

---

Questa guida ti fornisce una panoramica completa e discorsiva su come impostare un ambiente di provisioning automatizzato usando strumenti moderni e compatibili con AWS.

