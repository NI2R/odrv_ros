#!/usr/bin/env python
# -*-coding:Latin-1 -*

from __future__ import print_function

# import MCP3008
# import odrive #pas utilisé ?
# import odrive.enums  # à checker
from interfaceROS import Robot_properties
from time import sleep
from math import pi


class Move:
    def __init__(self, odrv0):  # p1, p2
        # self.Treat = Treatment()
        # self.info_move = self.Treat.step(p1, p2)

        self.odrv = odrv0      # Assignation du odrive

        # Robot physical constant
        self.nbTicks = 8192    # Nombre de tics pr un tour d'encoder
        self.dRoue = 80     # Diamètre roue en mm
        self.pRoue = self.dRoue * pi  # Périmètre roue en mm
        self.entreAxe = 280    # entre-axe en mm

        # coding features
        self.errorMax = 10      # unité ?
        self.OBS = False        # Init  Ostacle Detecté
        self.ActDone = False     # Init Action Faite
        self.SenOn = list()

        # Appel de la classe Robot_properties dans interfaseROS.py
        self.Robot = Robot_properties()

    def wait_end_move(self, mouv, axis, goal, errorMax, senslist):
        ''' Fonction appelée à la fin des fonctions Move pour assurer
            l'execution complète du mouvement/déplacement. '''
        """ [EN TEST] CONDITIONS for Obstacle Avoidance System (OAS)"""
        # + la liste est petite + la condition du while lachera rapidement
        nb = 1
        avg = nb * [0]
        index = 0
        movAvg = abs(goal - axis.encoder.pos_estimate)
        diff_step = 0
        wd = 0
        self.ActDone = False
        # Pour lecture capteur en fonction du sens de Translation
        Sen = [0, 1, 2, 3, 4]
        self.SenOn = [0 for i in range(len(Sen))]

        while movAvg >= errorMax:
            # Fonction pour afficher l'angle ou le déplacement instantannée
            # du robot
            if mouv == "rot":
                angleInst = (- 360.0 * self.pRoue * axis.encoder.pos_estimate)\
                 / (pi * self.entreAxe * self.nbTicks)
                # print("Angle du Robot : %.2f°" % angleInst)

            elif mouv == "trans":
                distInst0 = \
                 (axis.encoder.pos_estimate * self.pRoue) \
                 / self.nbTicks
                # print("Déplacement du Robot : %.2f mm" % distInst0)

                sleep(1)

                distInst1 = (axis.encoder.pos_estimate * self.pRoue) / self.nbTicks
                # print("Déplacement du Robot : %.2f mm" % distInst1)

                vitMoteur = (distInst1 - distInst0) / 1000

                """ PUBLICATIONS ROS : """
                self.Robot.update_Distance_parc(distInst0)

                if axis == 0:
                    self.Robot.update_Vitesse0(vitMoteur)
                else:
                    self.Robot.update_Vitesse1(vitMoteur)



            Sen_count = 0
            # print("Values vaut : ", MCP3008.readadc(1) )
            # print("Encoder : ", axis.encoder.pos_estimate,"Goal/Target : "
            # , goal, "movAvg : ", movAvg)

            """ Fonctions pour l'OAS """
            """for i in range(len(Sen)):
                if senslist[i] is True:
                    if MCP3008.readadc(Sen[i]) > 700:  # 600 trop de detection
                        self.OBS = True
                        self.SenOn[i] = 1
                        # print("Obstacle détécté")
                        # self.detect_obs(axis, goal)
                        # "print("Values vaut : ", MCP3008.readadc(Sen[i])

            for i in self.SenOn:
                if i != 0:
                    Sen_count += 1
            if Sen_count == 0:
                self.OBS = False
                for i in range(index, nb):
                    avg[i] = abs(goal - axis.encoder.pos_estimate)
                movAvg = 0
                for i in range(0, nb):
                    movAvg += avg[i] / nb
                diff_step = fabs(axis.encoder.pos_estimate - axis.encoder.pos_estimate)
                # print(diff_step)
                if diff_step < 10:
                    wd += 1
                    if wd > 200:
                        self.ActDone = True
                        return
                else:
                    wd = 0

                ## boucle d'accélération waitendmove
                #if self.buffer == movAvg:
                #    self.seuil += 1
                #    print("seuil =",self.seuil)
                #    if self.seuil > 100:
                #        self.seuil = 0
                #        axis0.controller.move_to_pos(2000,True)
                #        axis1.controller.move_to_pos(-2000,True)
                #        time.sleep(0.3)
                #else:
                #    self.seuil = 0

            self.buffer = movAvg
            # print("seuil =", self.seuil)
            elif Sen_count != 0:
                return
            """
        self.ActDone = True

    def rotation(self, angle, senslist):
        ''' [ Fonction qui fait tourner le robot sur lui même
            d'un angle donné en degré ] '''

        # Variables Locales :
        axis0 = self.odrv.axis0
        axis1 = self.odrv.axis1
        # Flag Mouvement rotation
        mouv = "rot"

        print("Lancement d'une Rotation de %.0f°" % angle)
        # calcul des ticks/pas à parcourir pour tourner

        distAngulaire = ((self.entreAxe/2) * angle * (pi / 180) \
                         * self.nbTicks)/self.pRoue


        # Assignation de values avec valeur du capteur IR
        # values = MCP3008.readadc(1)

        while 1:

            if self.OBS is False and self.ActDone is False:
                axis0.controller.move_to_pos(distAngulaire)
                axis1.controller.move_to_pos(distAngulaire)

                # Attente fin de mouvement SI aucun obstacle détécté
                self.wait_end_move(mouv, axis0, distAngulaire, self.errorMax,
                                   senslist)
                self.wait_end_move(mouv, axis1, distAngulaire, self.errorMax,
                                   senslist)
                # print("Rotation : Pas d'Obstacle")

            # fonction lié à l'OAS
            elif self.OBS is True and self.ActDone is False:
                self.stop()
                sleep(0.5)
                self.OBS = False
                print("Rotation : Obstacle")
            else:
                print("Rotation Terminée !")
                self.ActDone = False
                break

    def translation(self, distance, senslist):
        ''' [Fonction qui permet d'avancer droit pour une distance
            donnée en mm] '''

        # Variables Locales :
        axis0 = self.odrv0.axis0
        axis1 = self.odrv0.axis1
        # Flag Mouvement Translation :
        mouv = "trans"

        # Def. de la distance parcouru par les roues avant nouveau deplacement
        distInit0 = (axis0.encoder.pos_estimate * self.pRoue) \
            / self.nbTicks
        distInit1 = (axis1.encoder.pos_estimate * self.pRoue) \
            / self.nbTicks

        print("Lancement d'une Translation de %.0f mm" % distance)

        # Controle de la Position Longit en Absolu:
        target0 = axis0.encoder.pos_estimate - (self.nbTicks * distance) \
            / self.pRoue

        # Distance / Perimètre = nb tour a parcourir
        target1 = axis1.encoder.pos_estimate + (self.nbTicks * distance) \
            / self.pRoue

        # Action ! :
        """ [A inclure fonction évitement (OBS = True)] """
        """--------------------------------------------"""
        while 1:  # [A tester] (a la place de condition en dessous)
            # axis0.encoder.pos_estimate != target0 :
            # or axis1.encoder.pos_estimate != target1:

            if self.OBS is False and self.ActDone is False:
                axis0.controller.move_to_pos(target0)
                axis1.controller.move_to_pos(target1)
                # Attente fin de mouvement SI aucun obstacle détécté
                self.wait_end_move(mouv, axis0, target0, self.errorMax,
                                   senslist)
                self.wait_end_move(mouv, axis1, target1, self.errorMax,
                                   senslist)

                # print("Translation : Pas d'Obstacle")

            elif self.OBS is True and self.ActDone is False:
                self.stop()
                sleep(0.5)
                self.OBS = False
                print("Translation : Obstacle")
            else:
                print("Translation Terminée !")
                # Calcul et Affichage des nouveaux déplacements
                distRe0 = - distInit0 + \
                    (axis0.encoder.pos_estimate * self.pRoue)\
                    / self.nbTicks
                print("Distance Roue Gauche : %.4f " % distRe0)
                distRe1 = - distInit1 + \
                    (axis1.encoder.pos_estimate * self.pRoue)\
                    / self.nbTicks
                print("Distance Roue Droite : %.4f " % distRe1)
                self.ActDone = False
                break

    def stop(self):

        # Variables locales :
        axis0 = self.odrv0.axis0
        axis1 = self.odrv0.axis1

        # Met la vitessea des roues à 0.
        print("Le robot s'arrête")
        # axis0.controller.speed(0)
        # axis1.controller.speed(0)
        """ ou  POUR ARReTER LES MOTEURS : """

        axis0.controller.set_vel_setpoint(0, 0)
        axis1.controller.set_vel_setpoint(0, 0)
        axis0.controller.pos_setpoint = axis0.encoder.pos_estimate
        axis1.controller.pos_setpoint = axis1.encoder.pos_estimate

    def run(self):

        print("----------------<- 1 ROTATION ->----------------")
        self.rotation(self.Robot.Angle_int, [False, False, False, False, False])
        sleep(0.5)
        print("---------------<- 2 TRANSLATION ->---------------")
        self.translation(self.Robot.Dist_rect, [False, False, False, False, False])
        sleep(0.5)
        print("----------------<- 3 ROTATION ->----------------")
        self.rotation(self.Robot.Angle_fi, [False, False, False, False, False])
        print("=================================================")
