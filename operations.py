#Dokumentacja: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf


#Algorytm 1: Theta
def theta(A, w):
    #Inicjalizacja A'
    A_prime = [[[0] * w for _ in range(5)] for _ in range(5)]
    
    #1
    C = [[0] * w for _ in range(5)]
    for x in range(5):
        for z in range(w):
            parity = 0
            for y in range(5):
                parity ^= A[x][y][z]
            C[x][z] = parity

    #2
    D = [[0] * w for _ in range(5)]
    for x in range(5):
        for z in range(w):
            D[x][z] = C[(x - 1) % 5][z] ^ C[(x + 1) % 5][(z - 1) % w]

    #3
    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_prime[x][y][z] = A[x][y][z] ^ D[x][z]

    #4
    return A_prime


#Algorytm 2: Rho
def rho(A, w):
    #Inicjalizacja A'
    A_prime = [[[0] * w for _ in range(5)] for _ in range(5)]
    
    #1
    for z in range(w):
        A_prime[0][0][z] = A[0][0][z]
    
    #2
    x, y = 1, 0
    
    #3
    for t in range(24):
        #a
        r = ((t + 1) * (t + 2)) // 2
        for z in range(w):
            A_prime[x][y][z] = A[x][y][(z - r) % w]
        
        #b
        x, y = y, (2 * x + 3 * y) % 5
    
    #4
    return A_prime


#Algorytm 3: Pi
def pi(A, w):
    #Inicjalizacja A'
    A_prime = [[[0] * w for _ in range(5)] for _ in range(5)]
    
    #1
    for x in range(len(A)):
        for y in range(len(A[0])):
            for z in range(w):
                A_prime[x][y][z] = A[(x+3*y) % 5][x][z]
    
    #2
    return A_prime
    

#Algorytm 4: Chi
def chi(A, w):
    #Inicjalizacja A'
    A_prime = [[[0] * w for _ in range(5)] for _ in range(5)]
    
    #1
    for x in range(len(A)):
        for y in range(len(A[0])):
            for z in range(w):
                A_prime[x][y][z] = A[x][y][z] ^ ((A[(x + 1) % 5][y][z] ^ 1) & A[(x + 2) % 5][y][z])
    
    #2
    return A_prime
    
#Algorytm 5: rc
def rc(t):
    #1
    if t % 255 == 0:
        return 1
        
    #2
    R = [1] + [0] * 7
    
    #3
    for i in range(1, t % 255 + 1):
        R = [0] + R  #a
        R[0] ^= R[8] #b
        R[4] ^= R[8] #c
        R[5] ^= R[8] #d
        R[6] ^= R[8] #e
        
        R = R[:8]  #f
        
    # 4
    return R[0]
    

#Algorytm 6: Iota
def iota(A, ir, w):
    #1
    A_prime = [[[elem for elem in row] for row in plane] for plane in A]
    
    #2
    RC = [0] * w
    
    #3
    for j in range(int(w).bit_length()):
        RC[2**j - 1] = rc(j + 7 * ir)
        
    #4
    for z in range(w):
        A_prime[0][0][z] ^= RC[z]

    #5
    return A_prime
    