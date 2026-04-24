# Projet COFRAP - Guide d'Installation de l'Infrastructure Locale

Ce document détaille la procédure pour déployer l'infrastructure locale du projet COFRAP (Kubernetes, MariaDB, OpenFaaS) à l'aide de Minikube.

Veuillez suivre le guide correspondant à votre système d'exploitation.
## DÉPLOIEMENT SUR WINDOWS 10 / 11

Cette méthode est recommandée pour les postes de développement locaux. Elle s'appuie sur le gestionnaire de paquets de Windows (winget) et Docker Desktop.
### 1. Prérequis

#### Avoir activé la virtualisation dans le BIOS/UEFI.

#### Avoir installé et lancé Docker Desktop (avec le backend WSL 2 activé de préférence).

#### Un terminal (PowerShell ou Invite de commandes) ouvert en mode Administrateur.

### 2. Installation des outils de base

#### Exécutez les commandes suivantes dans votre terminal pour installer Minikube, Kubectl et Helm (le gestionnaire de paquets Kubernetes) : PowerShell

#### Installation de Minikube
    PowerShell > winget install Kubernetes.minikube

#### Installation de Kubectl (La télécommande Kubernetes)
    PowerShell > winget install Kubernetes.kubectl

#### Installation de Helm
    PowerShell > winget install Helm.Helm

⚠️ Important : Fermez et rouvrez votre terminal après ces installations pour que les variables d'environnement soient prises en compte.
### 3. Démarrage du cluster COFRAP

Nous allons créer un profil dédié nommé mspr2 pour isoler notre projet :


#### Démarrer le cluster avec 2 CPU, 4Go de RAM et 20Go de disque
    PowerShell > minikube start -p mspr2 --driver=docker --cpus=2 --memory=4096 --disk-size=20g

#### Activer le routeur réseau (Ingress)
    PowerShell > minikube addons enable ingress -p mspr2

### 4. Vérification

#### Assurez-vous que le cluster est opérationnel :
    PowerShell > minikube status -p mspr2
    PowerShell > kubectl get nodes

## DÉPLOIEMENT SUR LINUX (Ubuntu / Debian)

Cette méthode est recommandée pour l'installation sur une Machine Virtuelle (VM) ou un serveur baremetal.

### 1. Prérequis et installation de Docker

Le cluster a besoin du moteur Docker pour faire tourner ses conteneurs de manière isolée.


#### Mise à jour du système
    Bash > sudo apt-get update && sudo apt-get upgrade -y

#### Installation de Docker
    Bash > sudo apt-get install -y docker.io

#### Ajouter votre utilisateur au groupe Docker (pour éviter de taper sudo partout)
    Bash > newgrp docker
    Bash > sudo usermod -aG docker $USER

### 2. Installation de Minikube

#### Téléchargement et installation du binaire officiel :

    Bash > curl -LO https://storage.googleapis.com/minikube/releases/latest minikube-linux-amd64
    Bash > sudo install minikube-linux-amd64 /usr/local/bin/minikube
    Bash > rm minikube-linux-amd64

### 3. Installation de Kubectl et Helm

Téléchargement des outils de pilotage du cluster :


#### Installation de Kubectl
    Bash > curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    Bash > sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    Bash > rm kubectl

#### Installation de Helm
    Bash > curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    Bash > chmod 700 get_helm.sh
    Bash > ./get_helm.sh
    Bash > rm get_helm.sh

### 4. Démarrage du cluster COFRAP

Création de l'environnement de travail :


#### Démarrer le cluster avec le driver Docker
    Bash > minikube start -p mspr2 --driver=docker --cpus=2 --memory=4096 --disk-size=20g

#### Activer le routeur réseau (Ingress)
    Bash > minikube addons enable ingress -p mspr2

### 5. Vérification

#### Assurez-vous que le cluster est prêt à recevoir vos commandes :
    Bash > minikube status -p mspr2
    Bash > kubectl get nodes



## INSTALLATION DES SERVICES (Commun Win/Linux)

Une fois que Minikube tourne et que votre terminal est prêt, exécutez ces étapes pour déployer la base de données et le moteur Serverless.

#### 1. Déploiement de MariaDB (via Bitnami)

Nous utilisons Helm pour déployer une instance persistante de MariaDB.


#### Ajouter le catalogue Bitnami
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

#### Installer MariaDB avec les identifiants COFRAP
#### Remarque : les mots de passe sont ici simplifiés pour le POC
helm install mspr-mariadb bitnami/mariadb \
  --set auth.rootPassword=rootcofrap \
  --set auth.database=cofrap_db \
  --set auth.username=cofrap_user \
  --set auth.password="SuperProtect&dPassw0ord"
  
#### On check que ça tourne
    kubectl get pods

#### On récupère le nom du service (ici mspr-mariadb)
    PS C:\Projets\MSPR2> kubectl get svc
    NAME                    TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
    kubernetes              ClusterIP   10.96.0.1      <none>        443/TCP    43h
    mspr-mariadb            ClusterIP   10.96.237.39   <none>        3306/TCP   42h
    mspr-mariadb-headless   ClusterIP   None           <none>        3306/TCP   42h

#### Et donc dans le slack.yaml on aura
    functions:
        hello-python:
            lang: python3-http-debian
            handler: ./hello-python
            image: pabloescargot/hellopython:latest
            environment:
            DB_HOST: "mspr-mariadb.default.svc.cluster.local"
            DB_USER: "cofrap_user"
            DB_PASSWORD: "SuperProtect&dPassw0ord"
            DB_NAME: "cofrap_db"

### 2. Déploiement d'OpenFaaS (Moteur Serverless)

OpenFaaS nécessite des namespaces (dossiers) spécifiques pour séparer le système des fonctions utilisateur.

#### 1. Créer les dossiers isolés (Namespaces)
    apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

#### 2. Ajouter le catalogue OpenFaaS
    helm repo add openfaas https://openfaas.github.io/faas-netes/
    helm repo update

#### 3. Installer le moteur
    helm upgrade openfaas --install openfaas/openfaas \
    --namespace openfaas \
    --set generateBasicAuth=true

### 3. Accès à l'interface OpenFaaS

Le cluster est isolé par défaut. Pour accéder à l'interface graphique (Gateway) depuis votre navigateur (https://localhost:8080) :

#### Ouvrez un tunnel (Port-Forward) :
    kubectl port-forward -n openfaas svc/gateway 8080:8080

#### Récupérez le mot de passe admin :
##### Sur Windows (PowerShell) :
    
    PowerShell > $SECRET = kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}"
    [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($SECRET))

##### Sur Linux :
    Bash> echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)

## Installation de FaaS cli

### Sur Windows
    Télécharger le .exe sur https://github.com/openfaas/faas-cli/releases puis rajouter dans les variables d'environnement

### Sur Linux
    curl -sSL https://cli.openfaas.com | sudo sh


## Créer une fonction OpenFaaS

### Executer la commande suivante avec le nom du template python3-http et le nom de la fonction hello-python
    faas-cli new --lang python3-http-debian hello-python

### Executer le build pour créer l'image docker
    Powershell > wsl -u root
    (deploy puis supprimer l'image docker, puis "faas-cli rm hello-python" pour supprimer le cache de l'ancienne fonction)
    sur windows via (wsl): faas-cli build -f stack.yaml

    Et pour voir si ça a bien été créé: docker images | grep hello

### run avec (il fait le build en plus)
    (deploy puis supprimer l'image docker, puis "faas-cli rm hello-python" pour supprimer le cache de l'ancienne fonction)
    faas-cli up -f stack.yam

### Pour tester (même si on est pas obligé) on peut créer le conteneur:
    docker run -p -it 9090:8080 hello-python:latest
    ensuite
    docker inspect {id}

    récupérer l'IP et aller sur localhost:9090

### Pour voir les modifications en temps réel faire:
    faas-cli local-run --port 9090 --watch

### Il faut maintenant heberger sur dockerhub notre image en créant un nouveau repository
    Donc mettre image: pabloescargot/hellopython:latest dans stack.yaml
    Faire docker login
    puis: faas-cli publish

### Pour déployer: 
    faas-cli deploy

### Démarrer une BDD docker:
    docker run --name db -e MARIADB_DATABASE=dbfass -e MARIADB_ROOT_PASSWORD=password -d mariadb:latest
    (bien penser à rattacher au meme réseau openfaas et mariadb)