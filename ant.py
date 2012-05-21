import random

class obj_reader(object):

    def __init__(self, filename):
        self.elements = []
        fin = open(filename)
        fin.readline()
        for line in fin:
            line = line.replace('\n', '')
            self.elements += [[line_n for line_n in line.split(',') if line_n is not '']] 
        fin.close()

class ACOOpt(object):

    def __init__(self, n_ants=10, n_iter=100, alpha=0.5, rho=0.5):
        self.eta = dict()
        self.tau = dict()
        self.solBest = dict() # self.solBest[i] = (magazzino_k)
        
        self.costi = dict()
        
        self.dist = dict()

        self.n_ants = n_ants
        self.n_iter = n_iter
        self.alpha = alpha
        self.rho = rho

        self.tau0 = 0
        self.dmax = 0

        self.magaz = obj_reader("magazzini.csv")
        self.client = obj_reader("clienti.csv")
        
        self.f = obj_reader("distanze.csv")
        
        self.magazKeyPos = dict()
        self.clientKeyPos = dict()

        for line in self.f.elements:
            magazPos = int(line[0]) - 1
            clientPos = int(line[1]) - 1
            self.magazKeyPos[self.magaz.elements[magazPos][0]] = magazPos
            self.clientKeyPos[self.client.elements[clientPos][0]] = clientPos
            line[0] = self.magaz.elements[int(line[0]) -1][0]
            line[1] = self.client.elements[int(line[1]) -1][0]
            position = tuple([line[0], line[1]])
            self.dist[position] = int(line[2])
            if self.dist[position] > self.dmax:
                self.dmax = self.dist[position]

        self.tau0 = 2 * self.dmax

        for m in self.magaz.elements:
            for c in self.client.elements:
                position = (m[0], c[0])
                self.eta[position] = self.dmax - self.dist[position]
                self.tau[position] = self.tau0
        return

    def ant_search(self):
        zPop = dict() # costo suluzioni
        Pop = dict() # soluzioni dell'iterazione
        
        for iter_n in range(self.n_iter):
            for a in range(self.n_ants):
                zPop[a], Pop[a] = self.construct_sol(a)
                if zPop[a] < self.cost(self.solBest):
                    self.solBest = Pop[a]
            self.tau = self.updateTau(zPop, Pop)
            print "Iterazione ", iter_n, " -- valore : ", self.cost(self.solBest)
        
        magUse = dict()

        print "La soluzione trovata e' la seguente :"
        
        for k in self.solBest.keys():
            print "Cliente : ", k, " \t - Magazzino : ", self.solBest[k], "\t - Distanza : ", self.dist[(self.solBest[k], k)], "\t - Richiesta : ", self.client.elements[self.clientKeyPos[k]][1]
            if self.solBest[k] in magUse.keys():
                magUse[self.solBest[k]] = int(magUse[self.solBest[k]]) + int(self.client.elements[self.clientKeyPos[k]][1])
            else:
                magUse[self.solBest[k]] = int(self.client.elements[self.clientKeyPos[k]][1])
        
        for k in magUse.keys():
            print "Magazzino : ", k, "\tUtilizzo : ", magUse[k], "/", self.magaz.elements[self.magazKeyPos[k]][1]
            
        return

    def cost(self, pop):
        if len(pop) == 0: 
            return 100000000;
        #print "calcolo costo di "
        #print pop
        co = 0
        for k in pop.keys():
            position = tuple([pop[k], k])
            co += self.dist[position]
        #print "il costo e' ", co
        return co

    def construct_sol(self, a):
        ## ritorna una coppia costo, soluzione
        rc = dict()
        val = dict()
        solutionMag = dict()
        for m in self.magaz.elements:
            rc[m[0]] = int(m[1])
        for c in self.client.elements:
            for m in self.magaz.elements:
                if int(rc[m[0]]) > int(c[1]):
                    position = tuple([m[0], c[0]])
                    #print "ETAAAAAAAAAAAAA"
                    #print self.eta
                    #print "TAAAAAAAUUUUUUUUUU"
                    #print self.tau
                    val[m[0]] = self.alpha * self.eta[position] + (1-self.alpha) * self.tau[position]
                else:
                    val[m[0]] = 0
            #print "Per ", c[0], " i val sono "
            #print val
            solutionMag[c[0]] = self.montecarlo(val)
            rc[solutionMag[c[0]]] = int(rc[solutionMag[c[0]]]) - int(c[1])
        return (self.cost(solutionMag), solutionMag)

    def updateTau(self, zPop, Pop):
        # DEFINIZIONI
        # zPop = dict() # costo suluzioni
        # Pop = dict() # soluzioni dell'iterazione Pop[clientID] = magazID
        zWorst = 0
        for m in self.magaz.elements:
            for c in self.client.elements:
                self.tau[(m[0], c[0])] = self.rho * self.tau[(m[0], c[0])]
        
        for a in range(self.n_ants):
            if self.cost(Pop[a]) > zWorst:
                zWorst = self.cost(Pop[a])

        #print "ASFASFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        print "ZWORST ", zWorst

        #print Pop[3]
        #print zPop[3]
        #print self.cost(Pop[3])

        for a in range(self.n_ants):
            for c in self.client.elements:
                self.tau[Pop[a][c[0]], c[0]] += zWorst - zPop[a]
        return self.tau
    
    def montecarlo(self, val):
        # implementazione di selezione secondo montecarlo
        s = 0
#        print "VAL : " 
#        print val
        for i in val.keys():
#            print "chiave " + i
            s += val[i]
        r = s * random.random()
        s = 0
        k = None
        for i in val.keys():
            s += val[i]
            k = i
            if s>=r:
                break
        return k

    def write(self):
        fout = open("sol.csv", 'w')
        fout.write("mag, cli\n")
        for k in self.solBest.keys():
            fout.write(str(self.magazKeyPos[self.solBest[k]] + 1))
            fout.write(",")
            fout.write(str(self.clientKeyPos[k] + 1))
            fout.write("\n")
        fout.close()
        return

    

acosea = ACOOpt()

acosea.ant_search()
acosea.write()
