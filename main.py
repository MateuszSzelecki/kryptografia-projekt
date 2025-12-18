import math
from operations import theta, rho, pi, chi, rc, iota

class KeccakSponge:
    def __init__(self, rate, capacity, w, rounds):
        self.state_width = 25 * w
        if (rate+capacity) != self.state_width:
            raise ValueError(f"Błąd: rate ({rate}) + capacity ({capacity}) musi być równe {self.state_width} (25 * w)")
        self.rate = rate
        self.capacity = capacity
        self.w = w
        self.rounds = rounds
        self.bytes_per_lane = w // 8    #lane - ile bajtów ma jedna komórka macierzy
        self.rate_in_bytes = rate // 8  #rate - ile bajtów wchłaniamy w jednym cyklu

        self.state = [[[0] * w for _ in range(5)] for _ in range(5)]
        self.bufor = bytearray()

    def wykonaj_pojedyncza_runde(self, numer_rundy):
        self.state = theta(self.state, self.w)
        self.state = rho(self.state, self.w)
        self.state = pi(self.state, self.w)
        self.state = chi(self.state, self.w)
        self.state = iota(self.state, numer_rundy, self.w)
    
    def keccak_f(self):
        for i in range(self.rounds):
            self.wykonaj_pojedyncza_runde(i)

    def wchlanianie(self, input_bytes):
        self.bufor.extend(input_bytes)
        while len(self.bufor) >= self.rate_in_bytes:
            block = self.bufor[:self.rate_in_bytes]
            self.bufor = self.bufor[self.rate_in_bytes:]
            self.xorowanie_do_stanu(block)
            self.keccak_f()

    def wyciskanie(self, output_length_bytes):
        self.padding_i_wchlanianie()    #jesli cos jeszcze nie zostało wchłoniete bo to co w buforze mniejsze od rates_in_bytes
        output = bytearray()
        while len(output) < output_length_bytes:
            extracted = self.stan_na_bajty(self.rate_in_bytes)
            output.extend(extracted)
            if len(output) < output_length_bytes:
                self.keccak_f()
        return bytes(output[:output_length_bytes])

    def padding_i_wchlanianie(self):
        needed = self.rate_in_bytes - len(self.bufor)   #ile bajtów potrzeba do pełnego bloku
        pad_block = bytearray(self.bufor)
        if needed == 1: #tu w jednym bajcie będziemy zaczynali od 10 i konczyli na 01
            pad_block.append(0x86)
        else:
            pad_block.append(0x06)
            pad_block.extend(b'\x00' * (needed-2))
            pad_block.append(0x80)
        self.xorowanie_do_stanu(pad_block)
        self.keccak_f()
        
    def xorowanie_do_stanu(self, block_bytes): #zamieniamy bajty na macierz liczb całkowitych (zgodnie z 'w') i wkonuje XOR ze stanem
        input_lanes = []
        for i in range(0, len(block_bytes), self.bytes_per_lane):
            chunk = block_bytes[i:(i+self.bytes_per_lane)]
            if len(chunk) < self.bytes_per_lane:
                chunk += b'\x00' * (self.bytes_per_lane - len(chunk))
            val = int.from_bytes(chunk, 'little')
            input_lanes.append(val)
        idx = 0
        for y in range(5):
            for x in range(5):
                if idx < len(input_lanes):
                    val = input_lanes[idx]
                    for z in range(self.w): # rozbicie na bity
                        bit = (val >> z) & 1
                        self.state[x][y][z] ^= bit
                    idx += 1
                else: return

    def stan_na_bajty(self, length):
        out = bytearray()
        for y in range(5):
            for x in range(5):
                val = 0
                for z in range(self.w):
                    if self.state[x][y][z] == 1:
                        val |= (1 << z)
                lane_bytes = val.to_bytes(self.bytes_per_lane, 'little')
                out.extend(lane_bytes)
                if len(out) >= length: return out[:length]
        return out
    

if __name__ == "__main__":
    keccak = KeccakSponge(rate=1088, capacity=512, w=64, rounds=24)
    
    msg = b"krypto"
    keccak.wchlanianie(msg)
    digest = keccak.wyciskanie(32) # Pobieramy 32 bajty (256 bitów)
    
    print(f"Wejście: {msg}")
    print(f"Skrót (hex): {digest.hex()}")