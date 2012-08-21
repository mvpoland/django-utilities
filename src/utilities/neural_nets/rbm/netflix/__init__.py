import numpy as np
import random
import math

NMOVIES = 17770
SOFTMAX = 5
TOTAL_FEATURES = 100
NUSERS = 480189
NENTRIES = 103297638

vishid = 0.02 * np.random.randn(NMOVIES, SOFTMAX, TOTAL_FEATURES) - 0.01
visbiases = np.empty((NMOVIES, SOFTMAX,))
hidbiases = np.zeros(TOTAL_FEATURES)
CDpos = np.zeros((NMOVIES, SOFTMAX, TOTAL_FEATURES))
CDneg = np.zeros((NMOVIES, SOFTMAX, TOTAL_FEATURES))
CDinc = np.zeros((NMOVIES, SOFTMAX, TOTAL_FEATURES))

poshidprobs = np.empty(TOTAL_FEATURES)
poshidstates = [False] * TOTAL_FEATURES
curposhidstates = [False] * TOTAL_FEATURES
poshidact = np.zeros(TOTAL_FEATURES)
neghidact = np.zeros(TOTAL_FEATURES)
neghidprobs = np.empty(TOTAL_FEATURES)
neghidstates = [False] * TOTAL_FEATURES
hidbiasinc = np.zeros(TOTAL_FEATURES)

nvp2 = np.empty((NMOVIES, SOFTMAX))
negvisprobs = np.empty((NMOVIES, SOFTMAX))
neghidstates = [False] * NMOVIES
posvisact = np.zeros((NMOVIES, SOFTMAX))
negvisact = np.zeros((NMOVIES, SOFTMAX))
visbiasinc = np.zeros((NMOVIES, SOFTMAX))

moviercount = np.zeros(SOFTMAX * NMOVIES)
moviecount = np.zeros(NMOVIES)
negvissoftmax = [False] * NMOVIES

useridx = np.empty((NUSERS, 4))
userent = np.empty(NENTRIES)
err = np.empty[NENTRIES]

USER_MOVIEMASK = 0x7fff
USER_LMOVIEMASK = 15

epsilonw = 0.00075  # Learning rate for weights
epsilond = 0.000001  # Learning rate for Dij
epsilonvb = 0.003 # Learning rate for biases of visible units
epsilonhb = 0.0003 # Learning rate for biases of hidden units
momentum = 0.84  
finalmomentum = 0.9
weightcost = 0.0001

E = 0.00002

aopt = 0

NQUALIFY_SIZE = 2852071

def load_bin(path):
    fp = open(path, 'rb')
    length = 2852071 * 4
    print 'loading %s' % path
    buffer = fp.read(length)
    fp.close()
    return buffer
    
def untrain(u):
    return (useridx[u][1] + useridx[u][2]) if aopt else useridx[u][1]

def unall(u):
    return (useridx[u][1] + useridx[u][2] + useridx[u][3]) if aopt else (useridx[u][1] + useridx[u][2])

def score_setup():
    for m in range (0, NMOVIES):
        moviercount[m * SOFTMAX + 0] = 0
        moviercount[m * SOFTMAX + 1] = 0
        moviercount[m * SOFTMAX + 2] = 0
        moviercount[m * SOFTMAX + 3] = 0
        moviercount[m * SOFTMAX + 4] = 0
        
    for u in range(0, NUSERS):
        base0 = useridx[u][0];
        d0 = untrain(u)
            
        # For all rated movies
        for j in range(0, d0):
            m = userent[base0+j] & USER_MOVIEMASK
            r = (userent[base0+j] >> USER_LMOVIEMASK) & 7
            moviercount[m*SOFTMAX+r] += 1
        
def record_errors():
    for u in range(0, NUSERS):
        # Zero out the probability accumulator
        
        negvisprobs = np.zeros((NMOVIES, SOFTMAX))
        
        # Perform a training iteration on pure probabilities up to visible node reconstruction
        
        base0 = useridx[u][0]
        d0 = untrain(u)
        dall = unall(u)
        
        # For all rated movies, accumulate contributions to hidden units
        
        sumW = [0] * TOTAL_FEATURES
        
        for j in range(0, d0):
            m = userent[base0+j] & USER_MOVIEMASK
            
            # 1. get one data point from data set.
            # 2. use values of this data point to set state of visible neurons Si
            
            r = (userent[base0 + j] >> USER_LMOVIEMASK) & 7
            
            # for all hidden units h:
            for h in range(0, TOTAL_FEATURES):
                # sum_j(W[i][j] * v[0][j]))
                sumW[h] += vishid[m][r][h]
                
        for h in range(0, TOTAL_FEATURES):
            # 3. compute Sj for each hidden neuron based on formula above and states of visible neurons Si
            # compute Q(h[0][i] = 1 | v[0]) # for binomial units, sigmoid(b[i] + sum_j(W[i][j] * v[0][j]))
            poshidprobs[h] = 1.0 / (1.0 + math.exp(-sumW[h] - hidbiases[h]))
            
        # 5. on visible neurons compute Si using the Sj computed in step3. This is known as reconstruction
        # for all visible units j:
        
        count = dall,
        
        for j in range(0, count):
            m = userent[base0 + j] & USER_MOVIEMASK
            
            for h in range(0, TOTAL_FEATURES):
                for r in range(0, SOFTMAX):
                    negvisprobs[m][r] += poshidprobs[h] * vishid[m][r][h]
                    
            # compute P(v[1][j] = 1 | h[0]) # for binomial units, sigmoid(c[j] + sum_i(W[i][j] * h[0][i]))            
            negvisprobs[m][0]  = 1./(1 + math.exp(-negvisprobs[m][0] - visbiases[m][0]));
            negvisprobs[m][1]  = 1./(1 + math.exp(-negvisprobs[m][1] - visbiases[m][1]));
            negvisprobs[m][2]  = 1./(1 + math.exp(-negvisprobs[m][2] - visbiases[m][2]));
            negvisprobs[m][3]  = 1./(1 + math.exp(-negvisprobs[m][3] - visbiases[m][3]));
            negvisprobs[m][4]  = 1./(1 + math.exp(-negvisprobs[m][4] - visbiases[m][4]));
            
            # Normalize probabilities
            tsum = negvisprobs[m][0] + \
                   negvisprobs[m][1] + \
                   negvisprobs[m][2] + \
                   negvisprobs[m][3] + \
                   negvisprobs[m][4]
                   
            if tsum:
                negvisprobs[m][0] /= tsum;
                negvisprobs[m][1] /= tsum;
                negvisprobs[m][2] /= tsum;
                negvisprobs[m][3] /= tsum;
                negvisprobs[m][4] /= tsum;
        
        for i in range(0, dall):
            m = userent[base0 + i] & USER_MOVIEMASK
            r = (userent[base0 + i] >> USER_LMOVIEMASK) & 7
            expectedV = negvisprobs[m][1] + 2.0 * \
                        negvisprobs[m][2] + 3.0 * \
                        negvisprobs[m][3] + 4.0 * \
                        negvisprobs[m][4];
                        
            vdelta = r - expectedV;
            err[base0 + i] = vdelta;
            
def do_all_features():
    for j in range(0, NMOVIES):
        mtot = float(moviercount[j * SOFTMAX + 0] + \
                     moviercount[j * SOFTMAX + 1] + \
                     moviercount[j * SOFTMAX + 2] + \
                     moviercount[j * SOFTMAX + 3] + \
                     moviercount[j * SOFTMAX + 4])
               
        for i in range(0, SOFTMAX):
            visbiases[j][i] = math.log(float(moviercount[j * SOFTMAX + i]) / mtot)
            
    # Optimize current feature
    nrmse, last_rmse, prmse, last_prmse = 2., 10., 0, 0
    loopcount = 0
    
    EpsilonW = epsilonw
    EpsilonVB = epsilonvb
    EpsilonHB = epsilonhb
    Momentum = momentum
    
    tsteps = 1
    
    # Iterate through the model while the RMSE is decreasing 
    while (nrmse < (last_rmse-E) or loopcount < 14) and loopcount < 80:
        if loopcount >= 10:
            tsteps = 3 + (loopcount - 10) / 5
            
        last_rmse = nrmse
        last_prmse = prmse
        loopcount += 1
        ntrain = 0
        nrmse = 0.0
        s = 0.0
        n = 0
        
        if loopcount > 5:
            Momentum = finalmomentum
            
        for u in range(0, NUSERS):
            # Clear summations for probabilities
            negvisprobs = np.zeros((NMOVIES, SOFTMAX)) 
            nvp2 = np.zeros((NMOVIES, SOFTMAX))
            
            # perform steps 1 to 8
            base0 = useridx[u][0]
            d0 = untrain(u)
            dall = unall(u)
            
            # For all rated movies, accumulate contributions to hidden units
            sumW = np.zeros[TOTAL_FEATURES]
            
            for j in range(0, d0):
                m = userent[base0+j] & USER_MOVIEMASK;
                moviecount[m] += 1
                
                # 1. get one data point from data set.
                # 2. use values of this data point to set state of visible neurons Si
                
                r = (userent[base0 + j] >> USER_LMOVIEMASK) & 7
                
                # Add to the bias contribution for set visible units
                posvisact[m][r] += 1.0
                
                # for all hidden units h:
                for h in range(0, TOTAL_FEATURES):
                    # sum_j(W[i][j] * v[0][j]))
                    sumW[h] += vishid[m][r][h];
                    
            for h in range(0, TOTAL_FEATURES):
                # 3. compute Sj for each hidden neuron based on formula above and states of visible neurons Si
                # poshidprobs[h] = 1./(1 + exp(-V*vishid - hidbiases);
                # compute Q(h[0][i] = 1 | v[0]) # for binomial units, sigmoid(b[i] + sum_j(W[i][j] * v[0][j]))
                
                poshidprobs[h] = 1.0 / (1.0 + math.exp(-sumW[h] - hidbiases[h]))
                
                # sample h[0][i] from Q(h[0][i] = 1 | v[0])
                if poshidprobs[h] > np.random.rand():
                    poshidstates[h] = True
                    poshidact[h] += 1.0
                else:
                    poshidstates[h] = False
            
            # Load up a copy of poshidstates for use in loop
            curposhidstates = np.copy(poshidstates)
            
            # Make T Contrastive Divergence steps
            stepT = 0
            
            while True:
                # Determine if this is the last pass through this loop
                finalTStep = (stepT + 1 >= tsteps)
                
                # 5. on visible neurons compute Si using the Sj computed in step3. This is known as reconstruction
                # for all visible units j:
                
                count = d0
                count += useridx[u][2] # to compute probe errors
                
                for j in range(0, count):
                    m = userent[base0 + j] & USER_MOVIEMASK
                    
                    for h in range(0, TOTAL_FEATURES):
                        # Accumulate Weight values for sampled hidden states == 1
                        if curposhidstates[h]:
                            for r in range(0, SOFTMAX):
                                negvisprobs[m][r] += vishid[m][r][h]
                        
                        # Compute more accurate probabilites for RMSE reporting
                        
                        if stepT == 0:
                            for r in range(0, SOFTMAX):
                                nvp2[m][r] += poshidprobs[h] * vishid[m][r][h]
                        
                    # compute P(v[1][j] = 1 | h[0]) # for binomial units, sigmoid(c[j] + sum_i(W[i][j] * h[0][i]))
                    # Softmax elements are handled individually here
                    negvisprobs[m][0]  = 1./(1 + math.exp(-negvisprobs[m][0] - visbiases[m][0]));
                    negvisprobs[m][1]  = 1./(1 + math.exp(-negvisprobs[m][1] - visbiases[m][1]));
                    negvisprobs[m][2]  = 1./(1 + math.exp(-negvisprobs[m][2] - visbiases[m][2]));
                    negvisprobs[m][3]  = 1./(1 + math.exp(-negvisprobs[m][3] - visbiases[m][3]));
                    negvisprobs[m][4]  = 1./(1 + math.exp(-negvisprobs[m][4] - visbiases[m][4]));
                    
                    # Normalize probabilities
                    tsum  = negvisprobs[m][0] + \
                            negvisprobs[m][1] + \
                            negvisprobs[m][2] + \
                            negvisprobs[m][3] + \
                            negvisprobs[m][4]
                    
                    if tsum:
                        negvisprobs[m][0]  /= tsum;
                        negvisprobs[m][1]  /= tsum;
                        negvisprobs[m][2]  /= tsum;
                        negvisprobs[m][3]  /= tsum;
                        negvisprobs[m][4]  /= tsum;
                    
                    # Compute and Normalize more accurate RMSE reporting probabilities
                    if stepT == 0:
                        nvp2[m][0]  = 1./(1 + math.exp(-nvp2[m][0] - visbiases[m][0]));
                        nvp2[m][1]  = 1./(1 + math.exp(-nvp2[m][1] - visbiases[m][1]));
                        nvp2[m][2]  = 1./(1 + math.exp(-nvp2[m][2] - visbiases[m][2]));
                        nvp2[m][3]  = 1./(1 + math.exp(-nvp2[m][3] - visbiases[m][3]));
                        nvp2[m][4]  = 1./(1 + math.exp(-nvp2[m][4] - visbiases[m][4]));
                        
                        tsum2  = nvp2[m][0] + \
                                 nvp2[m][1] + \
                                 nvp2[m][2] + \
                                 nvp2[m][3] + \
                                 nvp2[m][4];
                                 
                        if tsum2:
                            nvp2[m][0]  /= tsum2;
                            nvp2[m][1]  /= tsum2;
                            nvp2[m][2]  /= tsum2;
                            nvp2[m][3]  /= tsum2;
                            nvp2[m][4]  /= tsum2;
                    
                    # sample v[1][j] from P(v[1][j] = 1 | h[0])
                    randval = np.random.rand()
                    
                    randval -= negvisprobs[m][0]
                    
                    if randval <= 0.0:
                        negvissoftmax[m] = 0
                    else:
                        randval -= negvisprobs[m][1]
                        
                        if randval <= 0.0:
                            negvissoftmax[m] = 1
                        else:
                            randval -= negvisprobs[m][2]
                        
                            if randval <= 0.0:
                                negvissoftmax[m] = 2
                            else:
                                randval -= negvisprobs[m][3]
                        
                                if randval <= 0.0:
                                    negvissoftmax[m] = 3
                                else:
                                    negvissoftmax[m] = 4
                    
                    # if in training data then train on it
                    if j < d0 and finalTStep:
                        negvisact[m][negvissoftmax[m]] += 1.0
                
                # 6. compute state of hidden neurons Sj again using Si from 5 step.
                # For all rated movies accumulate contributions to hidden units from sampled visible units
                
                sumW = np.zeros[TOTAL_FEATURES]
                for j in range(0, d0):
                    m = userent[base0 + j] & USER_MOVIEMASK
                    
                    # for all hidden units h:
                    for h in range(0, TOTAL_FEATURES):
                        sumW[h] += vishid[m][negvissoftmax[m]][h]
                
                # for all hidden units h:
                for h in range(0, TOTAL_FEATURES):
                    # compute Q(h[1][i] = 1 | v[1]) # for binomial units, sigmoid(b[i] + sum_j(W[i][j] * v[1][j]))
                    neghidprobs[h] = 1. / (1 + math.exp(-sumW[h] - hidbiases[h]))
                    
                    # Sample the hidden units state again.
                    if neghidprobs[h] > np.random.rand():
                        neghidstates[h] = True
                        
                        if finalTStep:
                            neghidact[h] += 1.0
                    else:                      
                        neghidstates[h] = False
                
                # Compute error rmse and prmse before we start iterating on T
                
                if stepT == 0:
                    # Compute rmse on training data
                    for j in range(0, d0):
                        m = userent[base0 + j] & USER_MOVIEMASK;
                        r = (userent[base0 + j] >> USER_LMOVIEMASK) & 7
                        
                        # # Compute some error function like sum of squared difference between Si in 1) and Si in 5)
                        expectedV = nvp2[m][1] + 2.0 * nvp2[m][2] + 3.0 * nvp2[m][3] + 4.0 * nvp2[m][4];
                        vdelta = r - expectedV
                        
                    ntrain += d0;
                    
                    # Sum up probe rmse
                    base = useridx[u][0]
                    for i in range(1, 2):
                        base += useridx[u][i]
                    d = useridx[u][2]
                    for i in range(0, d):
                        m = userent[base + i] & USER_MOVIEMASK
                        r = (userent[base + i] >> USER_LMOVIEMASK) & 7
                        
                        # # Compute some error function like sum of squared difference between Si in 1) and Si in 5)
                        expectedV = nvp2[m][1] + 2.0 * nvp2[m][2] + 3.0 * nvp2[m][3] + 4.0 * nvp2[m][4];
                        vdelta = r - expectedV
                        s += vdelta * vdelta
                        
                    n += d
                
                # If looping again, load the curposvisstates
                if not finalTStep:
                    curposhidstates = np.copy(neghidstates)
                    negvisprobs = np.zeros((NMOVIES, SOFTMAX))
                    
                # 8. repeating multiple times steps 5,6 and 7 compute (Si.Sj)n. Where n is small number and can 
                # increase with learning steps to achieve better accuracy.
                
                if stepT >= tsteps:
                    break
                
                stepT += 1
                
            # Accumulate contrastive divergence contributions for (Si.Sj)0 and (Si.Sj)T
            
            for j in range(0, d0):
                m = userent[base0 + j] & USER_MOVIEMASK
                r = (userent[base0 + j] >> USER_LMOVIEMASK) & 7
                
                # for all hidden units h:
                for h in range(0, TOTAL_FEATURES):
                    if poshidstates[h]:
                        # 4. now Si and Sj values can be used to compute (Si.Sj)0  here () means just values not average
                        # accumulate CDpos = CDpos + (Si.Sj)0
                        CDpos[m][r][h] += 1.0;
                    CDneg[m][negvissoftmax[m]][h] += float(neghidstates[h])
            
            # Update weights and biases after batch
            bsize = 100
            if (u+1) % bsize == 0 or (u + 1) == NUSERS:
                numcases = u % bsize
                numcases += 1
                
                # Update weights
                
                for m in range(0, NMOVIES):
                    if moviecount[m] == 0:
                        continue
                    
                    # for all hidden units h:
                    for h in range(0, TOTAL_FEATURES):
                        # for all softmax
                        for rr in range(0, SOFTMAX):
                            # At the end compute average of CDpos and CDneg by dividing them by number of data points.
                            # Compute CD = < Si.Sj >0  < Si.Sj >n = CDpos  CDneg
                            
                            CDp = CDpos[m][rr][h]
                            CDn = CDneg[m][rr][h];
                            
                            if not CDp == 0.0 or not CDn == 0.0:
                                CDp /= float(moviecount[m])
                                CDn /= float(moviecount[m])
                                
                                # Update weights and biases W = W + alpha*CD (biases are just weights to neurons that stay always 1.0)
                                # e.g between data and reconstruction.
                                
                                CDinc[m][rr][h] = Momentum * CDinc[m][rr][h] + EpsilonW * ((CDp - CDn) - weightcost * vishid[m][rr][h])
                                vishid[m][rr][h] += CDinc[m][rr][h];
                    
                    # Update visible softmax biases
                    # for all softmax
                    
                    for rr in range(0, SOFTMAX):
                        if not posvisact[m][rr] == 0.0 or not negvisact[m][rr] == 0.0:
                            posvisact[m][rr] /= float(moviecount[m])
                            negvisact[m][rr] /= float(moviecount[m])
                            visbiasinc[m][rr] = Momentum * visbiasinc[m][rr] + EpsilonVB * ((posvisact[m][rr] - negvisact[m][rr]))
                            visbiases[m][rr] += visbiasinc[m][rr];
                            
                    # Update hidden biases
                    
                    for h in range(0, TOTAL_FEATURES):
                        if not poshidact[h] == 0.0 or not neghidact[h] == 0.0:
                            poshidact[h] /= float(numcases)
                            neghidact[h] /= float(numcases)
                            hidbiasinc[h] = Momentum * hidbiasinc[h] + EpsilonHB * ((poshidact[h] - neghidact[h]))
                            hidbiases[h] += hidbiasinc[h];
                            
                    CDpos = np.zeros((NMOVIES, SOFTMAX, TOTAL_FEATURES))
                    CDneg = np.zeros((NMOVIES, SOFTMAX, TOTAL_FEATURES))
                    poshidact = np.zeros(TOTAL_FEATURES)
                    neghidact = np.zeros(TOTAL_FEATURES)
                    posvisact = np.zeros((NMOVIES, SOFTMAX))
                    negvisact = np.zeros((NMOVIES, SOFTMAX))
                    moviecount = np.zeros(NMOVIES)
            
            nrmse = math.sqrt(nrmse / ntrain)
            prmse = math.sqrt(s / n)
            print "%f\t%f" % (nrmse, prmse,)
            
            if TOTAL_FEATURES == 200:
                if loopcount > 6:
                    EpsilonW  *= 0.90
                    EpsilonVB *= 0.90
                    EpsilonHB *= 0.90
                elif loopcount > 5:    # With 200 hidden variables, you need to slow things down a little more
                    EpsilonW  *= 0.50  # This could probably use some more optimization
                    EpsilonVB *= 0.50
                    EpsilonHB *= 0.50
                elif loopcount > 2:
                    EpsilonW  *= 0.70
                    EpsilonVB *= 0.70
                    EpsilonHB *= 0.70
            else: # The 100 hidden variable case
                if loopcount > 8:
                    EpsilonW  *= 0.92
                    EpsilonVB *= 0.92
                    EpsilonHB *= 0.92
                elif loopcount > 6:
                    EpsilonW  *= 0.90
                    EpsilonVB *= 0.90
                    EpsilonHB *= 0.90
                elif loopcount > 2:
                    EpsilonW  *= 0.78
                    EpsilonVB *= 0.78
                    EpsilonHB *= 0.78
        
        # Perform a final iteration in which the errors are clipped and stored
        record_errors()