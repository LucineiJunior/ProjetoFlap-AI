import pygame
import os
import random
import neat

ai_jogando = True
geracao = 0

telalargura = 500
telaltura = 800
imgcano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
imgchao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
imgbg = pygame.transform.scale2x(pygame. image.load(os.path.join('imgs', 'bg.png')))
imgspass = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))]
pygame.font.init()
fontpontos = pygame.font.SysFont('arial', 50)


class Passaro:
    imagens = imgspass
    maxrot = 25
    velrot = 20
    tempoanim = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ang = 0
        self.vel = 0
        self.altura = self.y
        self.tempo = 0
        self.contagemimg = 0
        self.imagem = self.imagens[0]

    def pular(self):
        self.vel = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.vel * self.tempo
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2
        self.y += deslocamento
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.ang < self.maxrot:
                self.ang = self.maxrot
        else:
            if self.ang > 90:
                self.ang -= self.velrot

    def desenhar(self, tela):
        self.contagemimg += 1
        if self.contagemimg < self.tempoanim:
            self.imagem = self.imagens[0]
        elif self.contagemimg < self.tempoanim*2:
            self.imagem = self.imagens[1]
        elif self.contagemimg < self.tempoanim*3:
            self.imagem = self.imagens[2]
        elif self.contagemimg < self.tempoanim*4:
            self.imagem = self.imagens[1]
        elif self.contagemimg < self.tempoanim*4+1:
            self.imagem = self.imagens[0]
            self.contagemimg = 0

        if self.ang <= -80:
            self.imagem = self.imagens[1]
            self.contagemimg = self.tempoanim*2

        image_rotac = pygame.transform.rotate(self.imagem, self.ang)
        poscentroimg = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = image_rotac.get_rect(center=poscentroimg)
        tela.blit(image_rotac, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)

class Cano:
    distancia = 200
    velocidade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.postopo = 0
        self.posbase = 0
        self.canotopo = pygame.transform.flip(imgcano, False, True)
        self.canobase = imgcano
        self.passou = False
        self.defaltura()

    def defaltura(self):
        self.altura = random.randrange(50, 450)
        self.postopo = self.altura - self.canotopo.get_height()
        self.posbase = self.altura + self.distancia

    def mover(self):
        self.x -= self.velocidade

    def desenhar(self, tela):
        tela.blit(self.canotopo, (self.x, self.postopo))
        tela.blit(self.canobase, (self.x, self.posbase))

    def colidir(self, passaro):
        passaromask = passaro.get_mask()
        topomask = pygame.mask.from_surface(self.canotopo)
        basemask = pygame.mask.from_surface(self.canobase)
        distanciatopo = (self.x - passaro.x, self.postopo - round(passaro.y))
        distanciabase = (self.x - passaro.x, self.posbase - round(passaro.y))
        baseponto = passaromask.overlap(basemask, distanciabase)
        topoponto = passaromask.overlap(topomask, distanciatopo)
        if baseponto or topoponto:
            return True
        else:
            return False

class Chao():
    VELOCIDADE = 5
    LARGURA = imgchao.get_width()
    IMAGEM = imgchao

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhartela(tela, passaros, canos, chao, pontos):
    tela.blit(imgbg, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    texto = fontpontos.render(f'Pontos: {pontos}', 1, (255, 255, 255))
    tela.blit(texto, (telalargura - 10 - texto.get_width(), 10))
    if ai_jogando:
        texto = fontpontos.render(f'Geração: {geracao}', 1, (255, 255, 255))
        tela.blit(texto, (10, 10))
    chao.desenhar(tela)
    pygame.display.update()

def main(genomas, config):
    global geracao
    geracao += 1
    if ai_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))
    else:
        passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((telalargura, telaltura))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()
        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].canotopo.get_width()):
                indice_cano = 1
        else:
            rodando = False
            break
        for i, passaro in enumerate(passaros):
            passaro.mover()
            lista_genomas[i].fitness += 0.1
            output = redes[i].activate((passaro.y,
                                        abs(passaro.y - canos[indice_cano].altura),
                                        abs(passaro.y - canos[indice_cano].posbase)))
            if output[0] > 0.5:
                passaro.pular()
        chao.mover()

        adicionarcano = False
        removercanos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionarcano = True
            cano.mover()
            if cano.x + cano.canotopo.get_width() < 0:
                removercanos.append(cano)
        if adicionarcano:
            pontos += 1
            canos.append(Cano(600))
            for genoma in lista_genomas:
                genoma.fitness += 5
        for cano in removercanos:
            canos.remove(cano)
        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ai_jogando:
                    lista_genomas.pop(i)
                    redes.pop(i)
        desenhartela(tela, passaros, canos, chao, pontos)

def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
