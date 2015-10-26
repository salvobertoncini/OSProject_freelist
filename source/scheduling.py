# Salvatore Bertoncini 445857

import random
import sys
import copy
import datetime
import re

############################## CLASSI PRIMITIVE ##############################

#classe che rappresenta ogni singolo blocco (partizione) della memoria
class Blocco:
	#COSTRUTTORE
	def __init__(self, inizio, fine):
		self.inizio = inizio #rappresenta l'indice di inizio memoria occupata (il "byte" di memoria iniziale)
		self.fine = fine #rappresenta l'indice di fine memoria occupata (il "byte" di memoria finale)
		self.occupato = False #indica se il blocco di memoria e' stato assegnato a un processo (True) o e' libero (False, come da default)

	#GETTERS
	def dimensioneBlocco(self): #restituisce la dimensione del blocco semplicemente sottraendo fine ad inizio
		return (self.fine - self.inizio) 

#classe che rappresenta il singolo processo
class Processo:
	#COSTRUTTORE
	def __init__(self, dimensione, ingresso, tEsecuzione):
		self.dimensione = dimensione #rappresenta la dimensione del processo
		self.ingresso = ingresso #rappresenta il tempo di clock in cui il processo deve (se puo') entrare in esecuzione
		self.tEsecuzione = tEsecuzione #rappresenta quanti giri di clock necessita il processo per espletare le sue funzioni
		self.bloccoOccupato = None #rappresenta il blocco di memoria a cui e' stato assegnato il processo

#classe che rappresenta l'intera memoria
class Memoria: 
	#COSTRUTTORE
	def __init__(self, dimensione):
		self.dimensione = dimensione #rappresenta la dimensione totale della memoria, di default 1024
		self.reset ()

	def reset(self):
		self.blocchiMemoria = [] #rappresenta la lista di blocchi (partizioni) della memoria

		self.blocchiMemoria.append(Blocco(0,self.dimensione)) #crea il primo blocco unico di memoria

		self.freeList = []

		self.freeList.append(Blocco(0,self.dimensione))

############################## CLASSE LOG ##############################
#Classe per effettuare i print tutti assieme, senza dover scrivere i comandi piu' volte
class Log:
	def __init__(self, filename, permission):
		#Creo un file di log se non esiste. Altrimenti continuo a scrivere.
		self.log = open(filename + ".txt", permission)


	#Stampo il testo
	def write(self, text):
		#Print su shell
		print text

		#Log del testo su file senza colori
		self.log.write(text + "\n")

############################## FUNZIONI ##############################

def creaLista(): #metodo che crea la lista dei processi pronti
	numProcessi = random.randint(20,40) #numero dei processi pronti, randomico

	processiPronti = []

	for i in range(0, numProcessi):
		dimensione = random.randint(500,5000) #dimensione randomica processi
		ingresso = random.randint(0,20) #tempo di ingresso randomico
		tEsecuzione = random.randint(20,40) #tempo esecuzione randomico 
		processiPronti.append(Processo(dimensione, ingresso, tEsecuzione)) #inserisco il processi i-esimo creato nella lista

	return processiPronti

def bubbleSort(alist): #algoritmo bubblesort
    for passnum in range(len(alist)-1,0,-1):
        for i in range(passnum):
            if alist[i].ingresso>alist[i+1].ingresso:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp

def stampaMemoria(memoria): #stampa della memoria
	stampa.write("stampa della memoria!\n") 
	for i in range (0, len(memoria.blocchiMemoria)):
		if memoria.blocchiMemoria[i].occupato == True: #se il blocco di memoria e' libero stampa la sua dimensione dentro il simbolo pipe
			stampa.write("| "+str(memoria.blocchiMemoria[i].dimensioneBlocco())+" |\t")
		else: #altrimenti stampa il blocco di memoria dentro il simbolo cancelletto
			stampa.write("# "+str(memoria.blocchiMemoria[i].dimensioneBlocco())+" #\t")

def lifetimeProcessiEsecuzione(processiEsecuzione): #funzione che decrementa il lifetime di ogni processo in esecuzione di una unita'
	for i in range(0, len(processiEsecuzione)):
		processiEsecuzione[i].tEsecuzione -= 1

def verificaProcessiEsecuzione(memoria, processiEsecuzione): #verifica se nella lista dei processi pronti qualcuno di questi termina
	l = 0	#se termina, inserisce il blocco nella freeList, elimina il processo in esecuzione e libera la memoria occupata, 
	i = 0	#e unisce i blocchi di memoria liberi contigui
	numProcessi = len(processiEsecuzione)
	#for i in range(0, len(processiEsecuzione)):
	while(i<numProcessi):
		if processiEsecuzione[i].tEsecuzione == 0: #se il processo ha terminato la sua esecuzione
			indice = processiEsecuzione[i].bloccoOccupato # dentro la variabile di comodo mette il blocco di memoria da liberare
			indice.occupato = False #settata a False perche' si e' liberata

			#freelist
			memoria.freeList.append(processiEsecuzione[i].bloccoOccupato)

			del processiEsecuzione[i] #tolgo il processo in esecuzione
			numProcessi-=1 #decremento il numero dei processi in esecuzione
			
			unione(memoria) #unione dei blocchi liberi contigui

			stampa.write("processo terminato, stampa del nuovo stato di memoria")
			stampaMemoria(memoria)

			i-=1
			l+=1
		i+=1
	return l

def unione(memoria): #unione blocchi di memoria liberi contigui
	i = 0
	numBlocchi = len(memoria.blocchiMemoria)-1 
	while (i<numBlocchi): #scandaglio l'intera lista dei blocchi per vedere se ci sono blocchi contigui liberi
		if memoria.blocchiMemoria[i].occupato == False and memoria.blocchiMemoria[i+1].occupato == False: #se due blocchi sono liberi e contigui
			limite = memoria.blocchiMemoria[i+1].fine #salvo la fine del nuovo blocco di memoria prima di cancellarlo
			del memoria.blocchiMemoria[i+1]
			memoria.blocchiMemoria[i].fine = limite #memorizzo il nuovo limite 
			i-=1
			numBlocchi-=1
		i+=1

def split(memoria, i, processo, dimMemoria): #funzione che splitta i blocchi di memoria
	inizioPrimoBlocco = memoria.blocchiMemoria[i].inizio #salvo l'inizio del primo blocco
	splitPoint = inizioPrimoBlocco + processo.dimensione #salvo il punto di split, che funge da fine del primo e inizio del secondo blocco
	fineSecondoBlocco = memoria.blocchiMemoria[i].fine #salvo la fine del secondo blocco 

	del memoria.blocchiMemoria[i] #cancello il blocco di memoria da splittare

	bloccoSinistro = Blocco(inizioPrimoBlocco, splitPoint) #creo un blocco di memoria e lo setto occupato True
	bloccoSinistro.occupato = True

	bloccoDestro = Blocco(splitPoint, fineSecondoBlocco) #creo il secondo blocco

	memoria.blocchiMemoria.insert(i, bloccoSinistro) #inserirsco nella lista della memoria il primo blocco creato
	
	memoria.blocchiMemoria.insert(i+1, bloccoDestro) #inserisco nella lista della memoria, nell'indice successivo, il secondo blocco che sara' libero

def verificaFrammentazioneEsterna(dim_processo,blocchi):
	# inizializzo la seguente variabile che mi indica la dimensione dei blocchi liberi
	dim_blocchi = 0
	# inizializzo la seguente variabile che mi indica il blocco con la dimensione massima
	blocco_max = 0

	framm_esterna = 0
	i = 0
	# ciclo che termina alla fine dei blocchi di memoria e che mi permette di calcolare la dimensione di tutti i blocchi liberi
	while( i < len(blocchi.blocchiMemoria) ):
		# confornto se il blocco di memoria con indice i e' vuoto
		if( blocchi.blocchiMemoria[i].occupato == False ):
			# Incremente la variabile dim_blocchi con la dimensione del blocco di indice i vuoto
			dim_blocchi = dim_blocchi + blocchi.blocchiMemoria[i].dimensioneBlocco()
		i = i + 1


	i = 0
	# ciclo che mi permette di verificare qual'e' il blocco libero piu' grande tra i blocchi di memoria
	while( i < len(blocchi.blocchiMemoria) ):
		# condizione che mi permette di verificare se il bocco e' vuoto e se e' maggiore della variabile che indica la dimensione del blocco libero piu' grande
		if( blocchi.blocchiMemoria[i].occupato == False and blocchi.blocchiMemoria[i].dimensioneBlocco() > blocco_max ):
			# setto la variabile blocco_max con la dimensione del blocco libero piu' grande
			blocco_max = blocchi.blocchiMemoria[i].dimensioneBlocco()
		i = i + 1
	stampa.write("questo e' il blocco max: "+str(blocco_max)+"dimensione blocchi: "+str(dim_blocchi))		
	# Controllo se la dimensione dei blocchi liberi potrebbe contenere il processo che non e' stato allocato
	if( dim_blocchi >= dim_processo ):
		# Formula per il calcolo della frammentazione esterna
		stampa.write(str(blocco_max)+"  "+str(dim_blocchi))
		framm_esterna=(1.0 * 1)-(( 1.0 * blocco_max ) / ( 1.0 * dim_blocchi))
		# ritorno della variabile framm_esterna
		return framm_esterna
	return 0	

#stampa del menu iniziale
def menu():
	return int(raw_input("\nSELEZIONA METODO\n\n1- First Fit\n2- Best Fit\n3- Worst Fit\n4- Tutti i precedenti\n"))

############################## ALGORITMI FIT ##############################

def firstFit(memoria, processiPronti, dimMemoria):
	lifetime = len(processiPronti) #contiene i processi che prima o poi dovranno concludersi
	clock = 0 #contiene i cicli 

	comodo = 0 #flag che controlla l'allocazione del processo

	ver = 0
	# inizializzo inizialemente la variabile del contatore di confronti dei vari algoritmi
	count = 0
	# Inizializzo la variabile confronti che sara' settata a ogni chiamata dell'algoritmo che restituira' il numero di confronti effettuati
	confronti = 0
	# Inizializzo la variabile falliti che mi indica il numero delle allocazioni fallite
	falliti = 0
	# Inizializzo la variabile framm_esterne che mi indica il valore delle frammentazioni esterne
	framm_esterne = 0

	processiEsecuzione = [] #creo la lista dei processi in esecuzione

	stampa.write("\n@@@@@@@@@@ FIRST FIT @@@@@@@@@@\n")

	while len(processiPronti)>0 or lifetime>0: #se ci sono processi 
		lifetimeProcessiEsecuzione(processiEsecuzione) #richiamo la funzione che decrementa di uno il tempo di vita di ogni processo eseguito
		l = verificaProcessiEsecuzione(memoria, processiEsecuzione) #mi restituisce quanti processi eseguiti sono terminati
		lifetime -= l #toglie i processi terminati al totale dei processi da terminare
		if len(processiPronti)>0: #se ci sono processi pronti in coda
			confronti = 0 #inizializzo i confronti e il flag di entrata
			comodo = 0
			if(processiPronti[0].ingresso <= clock): #se il processo che deve entrare e' al giusto giro di clock (serve quasi solo all'inizio)
				stampa.write("ci sono processi che possono entrare perche' minori del clock")
				for i in range(0, len(memoria.blocchiMemoria)):
					stampa.write("siamo al passo "+str(i))
					confronti+=1 #incremento il confronto
					#se la memoria puo' ospitare il blocco ed e' libera
					if (memoria.blocchiMemoria[i].dimensioneBlocco() >= processiPronti[0].dimensione) and (memoria.blocchiMemoria[i].occupato == False):
						stampa.write("esiste un blocco vuoto e abbastanza capiente")
						#inserimento
						comodo = 1 #flag impostato a 1
						processiEsecuzione.append(processiPronti[0]) #il processo va in esecuzione
						stampa.write("\nprocesso selezionato: "+str(processiPronti[0].ingresso))
						indice = len(processiEsecuzione)-1
						split(memoria, i, processiEsecuzione[indice], dimMemoria) #split della memoria per ospitare il nuovo processo
						processiEsecuzione[indice].bloccoOccupato = memoria.blocchiMemoria[i] #salva il blocco della memoria occupato dentro il processo
						stampaMemoria(memoria)
						del processiPronti[0] #elimina il processo eseguito dalla coda dei pronti
						break

				if comodo == 0: #se non si e' modificato il flag qundi non si e' allocato il processo
					stampa.write("comodo non e' diventato 1")
					falliti+=1 #si incrementa il contatore dei falliti
					stampa.write("entro nella verifica della frammentazione")
					ver=verificaFrammentazioneEsterna(processiPronti[0].dimensione, memoria) #verifico se esiste frammentazione esterna 
					stampa.write("frammentazione esterna: "+str(ver))			

			else:
				stampa.write("\nALLOCAZIONE FALLITA! IMPOSSIBILE ESEGUIRE ALCUN PROCESSO CAUSA CLOCK: ")
				stampaMemoria(memoria)

			framm_esterne+=ver	#incremento le frammentazioni esterne
			count+=confronti #incremento i confronti

		stampa.write("\nclock: "+str(clock+1))
		clock += 1 #incremento il ciclo
		#
		stampa.write("\nlifetime: "+str(lifetime))
		
	if falliti>0: #se ci sono stati fallimenti 
		framm_esterne /= falliti #le frammentazioni esterne vengono divise per i fallimenti

	memoria.freeList = [] #libero la freelist

	#stampa.write("Il numero di confronti effettuati dall'algoritmo firstFit e' : "+str(count)+" con "+str(falliti)+" allocazioni fallite di cui "+str(framm_esterne)+"%  per frammentazioni esterne")
	return framm_esterne, count #ritorno le frammentazioni esterne e il contatore dei confronti

def bestFit(memoria, processiPronti, dimMemoria):
	lifetime = len(processiPronti) #contiene i processi che prima o poi dovranno concludersi
	clock = 0 #contiene i cicli 

	comodo = 0 #flag che controlla l'allocazione del processo

	ver = 0
	# inizializzo inizialemente la variabile del contatore di confronti dei vari algoritmi
	count = 0
	# Inizializzo la variabile confronti che sara' settata a ogni chiamata dell'algoritmo che restituira' il numero di confronti effettuati
	confronti = 0
	# Inizializzo la variabile falliti che mi indica il numero delle allocazioni fallite
	falliti = 0
	# Inizializzo la variabile framm_esterne che mi indica il valore delle frammentazioni esterne
	framm_esterne = 0

	processiEsecuzione = [] #creo la lista dei processi in esecuzione

	stampa.write("\n@@@@@@@@@@ BEST FIT @@@@@@@@@@\n")

	while len(processiPronti)>0 or lifetime>0:

		valIndice = -1 #confronto indice minimo
		valConfronto = 9999999999 #confronto valore minimo

		lifetimeProcessiEsecuzione(processiEsecuzione)
		l = verificaProcessiEsecuzione(memoria, processiEsecuzione)
		lifetime -= l

		if len(processiPronti)>0: #se ci sono processi pronti
			confronti = 0 #inizializzo i confronti e il flag di entrata
			comodo = 0
			if (processiPronti[0].ingresso <= clock): #se il processo che deve entrare e' al giusto giro di clock (serve quasi solo all'inizio)
				for i in range(0, len(memoria.blocchiMemoria)): 
					confronti+=1 #incremento il confronto
					#se la memoria puo' ospitare il blocco ed e' libera
					if (memoria.blocchiMemoria[i].dimensioneBlocco() >= processiPronti[0].dimensione) and (memoria.blocchiMemoria[i].occupato == False):
						#se la dimensione del blocco e' quella piu' piccola si salva indice compreso
						if valConfronto > memoria.blocchiMemoria[i].dimensioneBlocco():
							valIndice = i
							valConfronto = memoria.blocchiMemoria[i].dimensioneBlocco()
				if valIndice != -1: #se ha trovato un blocco piccolo piu' piccolo possibile
					#inserimento
					comodo = 1 #flag trovato a 1
					processiEsecuzione.append(processiPronti[0]) #eseguo il processo
					stampa.write("\nprocesso selezionato: "+str(processiPronti[0].ingresso))
					indice = len(processiEsecuzione)-1
					split(memoria, valIndice, processiEsecuzione[indice], dimMemoria) #splitto la memoria per ospitare il processo
					processiEsecuzione[indice].bloccoOccupato = memoria.blocchiMemoria[valIndice] #salva il blocco della memoria occupato dentro il processo
					stampaMemoria(memoria)
					del processiPronti[0] #elimina il processo eseguito dalla coda dei pronti
				#
				if comodo == 0: #se non si e' modificato il flag qundi non si e' allocato il processo
					stampa.write("comodo non e' diventato 1")
					falliti+=1 #si incrementa il contatore dei falliti
					stampa.write("entro nella verifica della frammentazione")
					ver=verificaFrammentazioneEsterna(processiPronti[0].dimensione, memoria) #verifico se esiste frammentazione esterna 
					stampa.write("frammentazione esterna: "+str(ver))
			else:
				stampa.write("\nALLOCAZIONE FALLITA! IMPOSSIBILE ESEGUIRE ALCUN PROCESSO: ")
				stampaMemoria(memoria)

			framm_esterne+=ver	#incremento le frammentazioni esterne
			count+=confronti #incremento i confronti

			stampa.write("\nclock: "+str(clock+1))
			clock += 1 #incremento il ciclo

		stampa.write("\nlifetime: "+str(lifetime))

	if falliti>0: #se ci sono stati fallimenti 
		framm_esterne /= falliti #le frammentazioni esterne vengono divise per i fallimenti

	memoria.freeList = [] #libero la freelist

	#stampa.write("Il numero di confronti effettuati dall'algoritmo firstFit e' : "+str(count)+" con "+str(falliti)+" allocazioni fallite di cui "+str(framm_esterne)+"%  per frammentazioni esterne")
	return framm_esterne, count

def worstFit(memoria, processiPronti, dimMemoria):
	lifetime = len(processiPronti) #contiene i processi che prima o poi dovranno concludersi
	clock = 0 #contiene i cicli 

	comodo = 0 #flag che controlla l'allocazione del processo

	ver = 0
	# inizializzo inizialemente la variabile del contatore di confronti dei vari algoritmi
	count = 0
	# Inizializzo la variabile confronti che sara' settata a ogni chiamata dell'algoritmo che restituira' il numero di confronti effettuati
	confronti = 0
	# Inizializzo la variabile falliti che mi indica il numero delle allocazioni fallite
	falliti = 0
	# Inizializzo la variabile framm_esterne che mi indica il valore delle frammentazioni esterne
	framm_esterne = 0

	processiEsecuzione = [] #creo la lista dei processi in esecuzione

	stampa.write("\n@@@@@@@@@@ WORST FIT @@@@@@@@@@\n")

	while len(processiPronti)>0 or lifetime>0:

		valIndice = -1 #confronto indice minimo
		valConfronto = None #confronto valore minimo

		lifetimeProcessiEsecuzione(processiEsecuzione)
		l = verificaProcessiEsecuzione(memoria, processiEsecuzione)
		lifetime -= l

		if len(processiPronti)>0: #se ci sono processi pronti
			confronti = 0 #inizializzo i confronti e il flag di entrata
			comodo = 0
			if (processiPronti[0].ingresso <= clock): #se il processo che deve entrare e' al giusto giro di clock (serve quasi solo all'inizio)
				for i in range(0, len(memoria.blocchiMemoria)): 
					confronti+=1 #incremento il confronto
					#se la memoria puo' ospitare il blocco ed e' libera
					if (memoria.blocchiMemoria[i].dimensioneBlocco() >= processiPronti[0].dimensione) and (memoria.blocchiMemoria[i].occupato == False):
						#se la dimensione del blocco e' quella piu' piccola si salva indice compreso
						if valConfronto < memoria.blocchiMemoria[i].dimensioneBlocco():
							valIndice = i
							valConfronto = memoria.blocchiMemoria[i].dimensioneBlocco()
				if valIndice != -1: #se ha trovato un blocco piccolo piu' piccolo possibile
					#inserimento
					comodo = 1 #flag trovato a 1
					processiEsecuzione.append(processiPronti[0]) #eseguo il processo
					stampa.write("\nprocesso selezionato: "+str(processiPronti[0].ingresso))
					indice = len(processiEsecuzione)-1
					split(memoria, valIndice, processiEsecuzione[indice], dimMemoria) #splitto la memoria per ospitare il processo
					processiEsecuzione[indice].bloccoOccupato = memoria.blocchiMemoria[valIndice] #salva il blocco della memoria occupato dentro il processo
					stampaMemoria(memoria)
					del processiPronti[0] #elimina il processo eseguito dalla coda dei pronti
				#
				if comodo == 0: #se non si e' modificato il flag qundi non si e' allocato il processo
					stampa.write("comodo non e' diventato 1")
					falliti+=1 #si incrementa il contatore dei falliti
					stampa.write("entro nella verifica della frammentazione")
					ver=verificaFrammentazioneEsterna(processiPronti[0].dimensione, memoria) #verifico se esiste frammentazione esterna 
					stampa.write("frammentazione esterna: "+str(ver))
			else:
				stampa.write("\nALLOCAZIONE FALLITA! IMPOSSIBILE ESEGUIRE ALCUN PROCESSO: ")
				stampaMemoria(memoria)

			framm_esterne+=ver	#incremento le frammentazioni esterne
			count+=confronti #incremento i confronti

			stampa.write("\nclock: "+str(clock+1))
			clock += 1 #incremento il ciclo

		stampa.write("\nlifetime: "+str(lifetime))

	if falliti>0: #se ci sono stati fallimenti 
		framm_esterne /= falliti #le frammentazioni esterne vengono divise per i fallimenti

	memoria.freeList = [] #libero la freelist

	#stampa.write("Il numero di confronti effettuati dall'algoritmo firstFit e' : "+str(count)+" con "+str(falliti)+" allocazioni fallite di cui "+str(framm_esterne)+"%  per frammentazioni esterne")
	return framm_esterne, count

############################## MAIN ##############################

############### inizializzo file di log ###############

stampa = Log("log", "w")
stampa.write(datetime.datetime.now().strftime('Simulazione effettuata in data %d/%m/%Y alle ore %H:%M:%S'))

############### numero simulazioni ###############

stampa.write("\nIMMETTI NUMERO SIMULAZIONI\n")
simulazioni = int(raw_input())
stampa.write("hai scelto di fare "+str(simulazioni)+" simulazioni\n")

############### scelta menu ###############

i=0 #contatore per le simulazioni

scelta = menu() #menu scelta

while(scelta<1 or scelta>4): #se la scelta non e' coerente con le opzioni visualizzate la faccio riapparire
	scelta = menu()

if scelta==1: #se scelgo il first fit
	#inizializzo le variabili per le statistiche
	framm_esterne = 0
	frammEsterne = 0
	count = 0
	cCount = 0
	while (i<simulazioni): #finche' non finisco il numero di simulazioni da effettuare
		stampa.write("############################## simulazione numero "+str(i+1)+" ##############################")

		dimMemoria = 20480 #inizializzo la dimensione della memoria a 20480kb
		memoria = Memoria(dimMemoria) #creo la memoria

		processiPronti = creaLista() #creo la lista dei processi pronti
		stampa.write(str(len(processiPronti))+" processi iniziali")
		for j in range(0, len(processiPronti)): #stampo i processi pronti
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))

		stampa.write("\n")

		bubbleSort(processiPronti) #ordino i processi pronti per ingresso
		stampa.write(str(len(processiPronti))+" processi ordinati per ingresso")
		for j in range(0, len(processiPronti)): #stampo i processi pronti ordinati
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))
		
		#mi faccio tornare dal first fit la frammentazione esterna e il count...	
		framm_esterne, count = firstFit(memoria, processiPronti, dimMemoria)
		#...e ne faccio la media
		frammEsterne+=framm_esterne
		cCount+=count

		i+=1
	#riporto in percentuale e stampo
	cCount=(cCount*1.0/simulazioni*1.0)
	frammEsterne=(frammEsterne*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo first-fit e': "+str(cCount))
	stampa.write("e media "+str(round(frammEsterne,2))+"%  di  frammentazioni esterne\n")
	

elif scelta==2: #se scelgo il best fit
	#inizializzo le variabili di statistica
	framm_esterne = 0
	frammEsterne = 0
	count = 0
	cCount = 0
	while (i<simulazioni): #finche' ci sono simulazioni da effettuare
		stampa.write("############################## simulazione numero "+str(i+1)+" ##############################")

		dimMemoria = 20480 #inizializzo la dimensione della memoria a 20480kb
		memoria = Memoria(dimMemoria) #creo la memoria

		processiPronti = creaLista() #creo la lista dei processi pronti
		stampa.write(str(len(processiPronti))+" processi iniziali")
		for j in range(0, len(processiPronti)): #stampo la lista dei processi pronti
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))

		stampa.write("\n")

		bubbleSort(processiPronti) #ordino la lista per tempo di ingresso
		stampa.write(str(len(processiPronti))+" processi ordinati per ingresso")
		for j in range(0, len(processiPronti)): #e la stampo ordinata per tempo
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))
		
		#mi faccio tornare le frammentazioni e il count e ne faccio la media
		framm_esterne, count = bestFit(memoria, processiPronti, dimMemoria)
		frammEsterne+=framm_esterne
		cCount+=count

		i+=1

	#percentualizzo count e frammentazioni
	cCount=(cCount*1.0/simulazioni*1.0)
	frammEsterne=(frammEsterne*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo best-fit e': "+str(cCount))
	stampa.write("e media "+str(round(frammEsterne,2))+"%  di  frammentazioni esterne\n")

elif scelta==3: #se scelgo il worst fit
	#inizializzo le variabili di statistica
	framm_esterne = 0
	frammEsterne = 0
	count = 0
	cCount = 0
	while (i<simulazioni):#finche' ci sono simulazioni da effetuare
		stampa.write("############################## simulazione numero "+str(i+1)+" ##############################")

		dimMemoria = 20480 #inizializzo la dimensione della memoria a 20480kb
		memoria = Memoria(dimMemoria) #creo la memoria

		processiPronti = creaLista() #creo la lista dei processi pronti
		stampa.write(str(len(processiPronti))+" processi iniziali")
		for j in range(0, len(processiPronti)): #tampo la lista
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))

		stampa.write("\n")

		bubbleSort(processiPronti) #ordino la lista per ingressi
		stampa.write(str(len(processiPronti))+" processi ordinati per ingresso")
		for j in range(0, len(processiPronti)): #stampo la lista ordinata
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))
		
		#mi faccio restituire dall'algoritmo frammentazioni esterne e count e ne faccio la media
		framm_esterne, count = worstFit(memoria, processiPronti, dimMemoria)
		frammEsterne+=framm_esterne
		cCount+=count

		i+=1
	#percentualizzo count e frammentazioni e le stampo
	cCount=(cCount*1.0/simulazioni*1.0)
	frammEsterne=(frammEsterne*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo best-fit e': "+str(cCount))
	stampa.write("e media "+str(round(frammEsterne,2))+"%  di  frammentazioni esterne\n")

else:#se scelgo tutti e tre i fit contemporaneamente
	#inizializzo le variabili statistiche
	framm_esterneF = 0
	frammEsterneF = 0
	countF = 0
	cCountF = 0
	framm_esterneB = 0
	frammEsterneB = 0
	countB = 0
	cCountB = 0
	framm_esterneW = 0
	frammEsterneW = 0
	countW = 0
	cCountW = 0

	while (i<simulazioni): #finche' ci sono simulazioni da effettuare
		stampa.write("############################## simulazione numero "+str(i+1)+" ##############################")

		dimMemoria = 20480 #inizializzo la dimensione della memoria a 20480kb
		memoria = Memoria(dimMemoria) #creo la memoria

		processiPronti = creaLista() #creo la lista dei processi pronti
		stampa.write(str(len(processiPronti))+" processi iniziali")
		for j in range(0, len(processiPronti)): #stampo la lista
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))

		stampa.write("\n")

		bubbleSort(processiPronti) #ordino la lista per ingressi
		stampa.write(str(len(processiPronti))+" processi ordinati per ingresso")
		for j in range(0, len(processiPronti)): #stampo la lista ordinata
			stampa.write("ingresso: "+str(processiPronti[j].ingresso)+"\tdimensione: "+str(processiPronti[j].dimensione)+"\ttempo esecuzione: "+str(processiPronti[j].tEsecuzione))
		
		processiPronti2 = copy.deepcopy(processiPronti) #copio la lista per usarla nel best fit
		processiPronti3 = copy.deepcopy(processiPronti) #copio la lista per usarla nel worst fit

		#per ogni algoritmo di fit, mi faccio restituire frammentazioni e confronti e le sommo ai loro contatori rispettivi
		framm_esterneF, countF = firstFit(memoria, processiPronti, dimMemoria)
		frammEsterneF+=framm_esterneF
		cCountF+=countF

		framm_esterneB, countB = bestFit(memoria, processiPronti2, dimMemoria)
		frammEsterneB+=framm_esterneB
		cCountB+=countB

		framm_esterneW, countW = worstFit(memoria, processiPronti3, dimMemoria)
		frammEsterneW+=framm_esterneW
		cCountW+=countW

		i+=1

	#percentualizzo i risultati ottenuti e li stampo
	cCountF=(cCountF*1.0/simulazioni*1.0)
	frammEsterneF=(frammEsterneF*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo first-fit e': "+str(cCountF))
	stampa.write("e media "+str(round(frammEsterneF,2))+"%  di  frammentazioni esterne\n")

	cCountB=(cCountB*1.0/simulazioni*1.0)
	frammEsterneB=(frammEsterneB*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo best-fit e': "+str(cCountB))
	stampa.write("e media "+str(round(frammEsterneB,2))+"%  di  frammentazioni esterne\n")

	cCountW=(cCountW*1.0/simulazioni*1.0)
	frammEsterneW=(frammEsterneW*1.0/simulazioni*1.0)*100

	stampa.write("La media dei confronti effettuati dall'algoritmo worst-fit e': "+str(cCountW))
	stampa.write("e media "+str(round(frammEsterneW,2))+"%  di  frammentazioni esterne\n")
