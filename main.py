                                               /$$  /$$$$$$  /$$          
                                              | $$ /$$__  $$| $$          
  /$$$$$$$  /$$$$$$  /$$   /$$ /$$$$$$$   /$$$$$$$| $$  \__/| $$ /$$   /$$
 /$$_____/ /$$__  $$| $$  | $$| $$__  $$ /$$__  $$| $$$$    | $$| $$  | $$
|  $$$$$$ | $$  \ $$| $$  | $$| $$  \ $$| $$  | $$| $$_/    | $$| $$  | $$            par xm et sartome
 \____  $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$      | $$| $$  | $$
 /$$$$$$$/|  $$$$$$/|  $$$$$$/| $$  | $$|  $$$$$$$| $$      | $$|  $$$$$$$
|_______/  \______/  \______/ |__/  |__/ \_______/|__/      |__/ \____  $$
                                                                 /$$  | $$
                                                                |  $$$$$$/
                                                                 \______/ 
import os, re, shutil, subprocess, atexit
import pygame
import requests
import customtkinter as ctk
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

print("BIENVENUE, passer un bon moment sur SoundFly")

class LecteurMusiqueYouTube:
    """
    Classe pour lire de la musique depuis YouTube en utilisant Pygame.
    """

    def __init__(self, api_key):
        """
        Initialise une nouvelle instance de LecteurMusiqueYouTube.

        Attributs:
            playlist (list): Une liste de chansons dans la playlist.
            current_song (str): Le nom du fichier audio en cours de lecture.
            api_key (str): La clé API YouTube utilisée pour effectuer des recherches.
        """
        self.playlist = []
        self.current_song = None
        self.api_key = api_key
        pygame.init()  # Initialisation de Pygame pour la lecture audio

    def supprimer_mp4(self, fichier_mp4):
        """
        Supprime le fichier .mp4 après la conversion en .mp3.

        Args:
            fichier_mp4 (str): Le chemin du fichier .mp4 à supprimer.
        """
        try:
            os.remove(fichier_mp4)
        except FileNotFoundError:
            print(f"Le fichier {fichier_mp4} n'existe pas.")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier .mp4 : {e}")

    def nettoyer_nom_chanson(self, nom_chanson):
        """
        Nettoie le nom de la chanson pour qu'il ne contienne que des caractères valides pour les noms de fichiers.

        Args:
            nom_chanson (str): Le nom de la chanson à nettoyer.

        Returns:
            str: Le nom de la chanson nettoyé.
        """
        return re.sub(r'[\/:*?"<>|]', '', nom_chanson.replace(' ', '_'))

    def lister_musiques_telechargees(self):
        """
        Liste les musiques déjà téléchargées dans le répertoire "musique".

        Returns:
            list: Une liste des noms de fichiers audio MP3 téléchargés.
        """
        dossier_musique = os.path.join(os.path.dirname(__file__), "musique")  # Répertoire "musique"
        fichiers_mp3 = [fichier for fichier in os.listdir(dossier_musique) if fichier.endswith(".mp3")]
        return fichiers_mp3
    
    def jouer_musique(self, fichier_audio):
        self.lecteur.arreter_lecture()
        self.lecteur.jouer_chanson(fichier_audio)
        self.status_label.configure(text=f"En train de jouer : {fichier_audio}")

        # Check if a corresponding video exists and play it
        video_filename = fichier_audio.replace('.mp3', '.mp4')
        if os.path.exists(video_filename):
            self.afficher_video(video_filename)


    def rechercher_chanson(self, recherche):
        """
        Recherche une chanson sur YouTube en utilisant la clé API fournie.
        Args:
            recherche (str): Le terme de recherche pour la chanson.
        Returns:
            str or None: L'ID vidéo de la chanson trouvée ou None si aucune chanson n'est trouvée.
        """
        try:
            url = (f"https://www.googleapis.com/youtube/v3/search?key={self.api_key}&q={recherche}&type=video&part"
                f"=snippet")
            response = requests.get(url)
            data = response.json()
            video_id = None

            for item in data.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    break

            if video_id:
                return self.telecharger_chanson(video_id)  # Pass the video_id to telecharger_chanson
            else:
                print("Aucune vidéo trouvée.")
            return None
        except Exception as e:
            print(f"Erreur lors de la recherche : {e}")
            return None
        
    def telecharger_chanson(self, video_id, max_time=600):
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            nom_chanson = self.nettoyer_nom_chanson(yt.title)  # Nettoyez le nom de la chanson
            dossier_musique = os.path.join(os.path.dirname(__file__), "musique")  # Répertoire "musique"
            fichier_audio_mp3 = os.path.join(dossier_musique, f"{nom_chanson}.mp3")

            # Check if the video duration exceeds max_time
            if yt.length > max_time:
                print(f"La durée de la vidéo dépasse le temps maximum de {max_time} secondes.")
                return None

            # Vérifier si le fichier MP3 existe déjà
            if os.path.isfile(fichier_audio_mp3):
                print(f"La musique '{nom_chanson}' est déjà téléchargée.")
                return fichier_audio_mp3

            stream = yt.streams.filter(only_audio=True).first()

            stream.download(output_path=dossier_musique, filename=f"{nom_chanson}.mp4")

            # Convertir le fichier MP4 en MP3
            fichier_audio_mp4 = os.path.join(dossier_musique, f"{nom_chanson}.mp4")
            ffmpeg_extract_audio(fichier_audio_mp4, fichier_audio_mp3)

            # Supprimer le fichier MP4
            self.supprimer_mp4(fichier_audio_mp4)

            return fichier_audio_mp3
        except Exception as e:
            print(f"Erreur lors du téléchargement et de la conversion de la chanson : {e}")
            return None
    
    def jouer_chanson(self, video_url):
        """
        Joue une chanson à partir du fichier audio MP3.

        Args:
            video_url (str): Le chemin du fichier audio MP3 à jouer.
        """
        try:
            self.current_song = os.path.basename(video_url)
            pygame.mixer.music.load(video_url)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Erreur lors de la lecture de la chanson : {e}")

    def arreter_lecture(self):
        """Arrête la lecture de la chanson en cours."""
        pygame.mixer.music.stop()
        self.current_song = None


class LecteurMusiqueApp(ctk.CTk):
    """
    Application du lecteur de musique YouTube avec une interface utilisateur.
    """

    max_music_per_page = 5  # Définissez le nombre maximal de musiques par page ici

    def __init__(self, api_key):
        """
        Initialise une nouvelle instance de LecteurMusiqueApp.

        Args:
            api_key (str): La clé API YouTube utilisée pour effectuer des recherches.
        """
        super().__init__()
        atexit.register(self.cleanup_on_exit)

        # Vérifiez si le dossier "musique" existe, sinon, créez-le
        dossier_musique = os.path.join(os.path.dirname(__file__), "musique")
        if not os.path.exists(dossier_musique):
            os.makedirs(dossier_musique)

        self.title("Lecteur de Musique YouTube")
        self.geometry("820x520")
        self.resizable(width=False, height=False)

        self.lecteur = LecteurMusiqueYouTube(api_key)
        self.current_page = 0  # Page actuelle des musiques téléchargées

        # Créez les widgets ici
        self.label = ctk.CTkLabel(self, text="Entrez le nom de la chanson à rechercher:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.chanson_entry = ctk.CTkEntry(self)
        self.chanson_entry.grid(row=0, column=1, padx=10, pady=10)

        self.rechercher_button = ctk.CTkButton(self, text="Télécharger une chanson", command=self.rechercher_chanson)
        self.rechercher_button.grid(row=0, column=2, padx=10, pady=10)

        self.afficher_button = ctk.CTkButton(self, text="Afficher les musiques déjà téléchargées",
                                             command=self.afficher_musiques_telechargees)
        self.afficher_button.grid(row=1, column=0, padx=10, pady=10)

        self.arreter_button = ctk.CTkButton(self, text="Pause", command=self.arreter_lecture)
        self.arreter_button.grid(row=1, column=1, padx=10, pady=10)

        self.quitter_button = ctk.CTkButton(self, text="Quitter", command=self.quitter)
        self.quitter_button.grid(row=1, column=2, padx=10, pady=10)

        self.supprimer_button = ctk.CTkButton(self, text="Effacer les musiques", command=self.nettoyer_musique)
        self.supprimer_button.grid(row=1, column=3, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.volume)
        self.volume_slider.grid(row=8, column=0, padx=10, pady=10,sticky="w")
        
        self.selectionner_mp3_button = ctk.CTkButton(self, text="Ouvrir un fichier local", command=self.selectionner_mp3)
        self.selectionner_mp3_button.grid(row=0, column=3, padx=10, pady=10)

    def selectionner_mp3(self):
        """
        Ouvre une boîte de dialogue pour sélectionner un fichier MP3 depuis l'ordinateur
        et le copie dans le répertoire "musique".
        """
        file_path = ctk.filedialog.askopenfilename(filetypes=[("Fichiers MP3", "*.mp3")])

        if file_path:
            # Copie le fichier sélectionné dans le répertoire "musique"
            file_name = os.path.basename(file_path)
            dossier_musique = os.path.join(os.path.dirname(__file__), "musique")
            destination_path = os.path.join(dossier_musique, file_name)
            shutil.copy(file_path, destination_path)

            self.status_label.configure(text=f"MP3 ajouté avec succès : {file_name}")
        
        
    def volume(self, volume):
        """
        Methode qui permet de faire fonctionner le bouton du son.

        Args:
            volume (str): Le volume du slider.
        """
        try:
            volume = int(volume)
        except ValueError:
            return
        pygame.mixer.music.set_volume(volume / 100)
    
    def raccourcir_nom_musique(self, nom_musique, longueur_max=20):
        """
        Raccourcit un nom de musique si sa longueur dépasse la longueur maximale spécifiée.

        Args:
            nom_musique (str): Le nom de la musique.
            longueur_max (int): La longueur maximale du nom de musique (par défaut : 20).

        Returns:
            str: Le nom de la musique raccourci.
        """
        if len(nom_musique) > longueur_max:
            return nom_musique[:longueur_max] + "..." + "mp3"
        else:
            return nom_musique

    def ajouter_bouton_retour(self):
        '''
        bouton permettant de remonter en haut de page.
        '''
        bouton_retour = ctk.CTkButton(self, text="↑", command=self.afficher_page_principale)
        bouton_retour.grid(row=self.max_music_per_page + 3, column=2, padx=30, pady=5, sticky="w")

    def afficher_page_principale(self):
        """
        Affiche la page principale en supprimant les éléments de la page précédente.
        """
        widgets = self.grid_slaves()
        for widget in widgets:
            widget.grid_forget()

        self.label.grid(row=0, column=0, padx=10, pady=10)
        self.chanson_entry.grid(row=0, column=1, padx=10, pady=10)
        self.rechercher_button.grid(row=0, column=2, padx=10, pady=10)
        self.afficher_button.grid(row=1, column=0, padx=10, pady=10)
        self.arreter_button.grid(row=1, column=1, padx=10, pady=10)
        self.quitter_button.grid(row=1, column=2, padx=10, pady=10)
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.volume_slider.grid(row=8, column=0, padx=10, pady=10)
        self.supprimer_button.grid(row=1, column=3, padx=10, pady=10)
        self.selectionner_mp3_button.grid(row=0, column=3, padx=10, pady=10)

    def rechercher_chanson(self):
        """
        Recherche et joue une chanson en utilisant l'entrée de l'utilisateur.
        """
        recherche = self.chanson_entry.get()
        video_id = self.lecteur.rechercher_chanson(recherche)
        if video_id:
            fichier_audio = self.lecteur.rechercher_chanson(recherche)
            if fichier_audio:
                self.status_label.configure(text=f"Musique téléchargée ici : {fichier_audio}")

    def afficher_musiques_telechargees(self):
        """
        Affiche les musiques déjà téléchargées dans l'interface avec un bouton "Jouer" pour chaque musique.
        """
        musiques_telechargees = self.lecteur.lister_musiques_telechargees()
        if musiques_telechargees:
            self.status_label.configure(text="Musiques déjà téléchargées :")
            self.ajouter_bouton_retour()

            # Calculer le début et la fin de la page actuelle
            debut_page = self.current_page * self.max_music_per_page
            fin_page = debut_page + self.max_music_per_page

            # Limiter les musiques à afficher à la page actuelle
            musiques_a_afficher = musiques_telechargees[debut_page:fin_page]

            for i, fichier_audio in enumerate(musiques_a_afficher):
                bouton_jouer = ctk.CTkButton(self, text="Jouer",
                                             command=lambda fichier=fichier_audio: self.jouer_musique(fichier))
                bouton_jouer.grid(row=i + 3, column=0, padx=10, pady=10, sticky="w")
                label_musique = ctk.CTkLabel(self, text=self.raccourcir_nom_musique(fichier_audio))
                label_musique.grid(row=i + 3, column=1, padx=10, pady=10, sticky="w")

                # Afficher les boutons "Suivant" et "Précédent" si nécessaire
                if len(musiques_telechargees) > self.max_music_per_page:
                    bouton_suivant = ctk.CTkButton(self, text="Suivant", command=self.page_suivante)
                    bouton_suivant.grid(row=9, column=1, padx=10, pady=10, sticky="e")

                    bouton_precedent = ctk.CTkButton(self, text="Précédent", command=self.page_precedente)
                    bouton_precedent.grid(row=9, column=0, padx=10, pady=10, sticky="e")
        else:
            self.status_label.configure(text="Aucune musique déjà téléchargée.")

    def nettoyer_musique(self):
        """
        Nettoie le dossier musique en supprimant tous les fichiers MP3.
        """
        dossier_musique = os.path.join(os.path.dirname(__file__), "musique")  # Répertoire "musique"
        fichiers_mp3 = [fichier for fichier in os.listdir(dossier_musique) if fichier.endswith(".mp3")]

        for fichier in fichiers_mp3:
            chemin_fichier = os.path.join(dossier_musique, fichier)
            try:
                subprocess.run(["taskkill", "/f", "/im", "ffmpeg-win64-v4.2.2.exe"], stderr=subprocess.DEVNULL)
                os.remove(chemin_fichier)
                subprocess.Popen("ffmpeg-win64-v4.2.2.exe")
                
            except:
                print("")

        self.status_label.configure(text="Dossier musique nettoyé (Redémarrer l'application pour appliquer).")
        

    def jouer_musique(self, fichier_audio):
        # Jouez la musique à partir du fichier audio MP3
        """
        Args:
            fichier_audio (str): prend le nom du fichier audio pour pouvoir le lire
        """
        self.lecteur.arreter_lecture()
        self.lecteur.jouer_chanson(fichier_audio)
        self.status_label.configure(text=f"En train de jouer : {fichier_audio}")

    def arreter_lecture(self):
        """
        Arrête Pygame et quitte l'application.
        """
        self.lecteur.arreter_lecture()

    def quitter(self):
        """
        Arrête Pygame et quitte l'application.
        """
        pygame.quit()
        self.quit()

    def page_suivante(self):
        """
        Affiche la page suivante des musiques téléchargées.
        """
        self.current_page += 1
        self.afficher_musiques_telechargees()

    def page_precedente(self):
        """
        Affiche la page précédente des musiques téléchargées.
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.afficher_musiques_telechargees()
    
    def cleanup_on_exit(self):
        """
        Ferme pygame et ffmpeg pour eviter les erreurs de conversion.
        """
        try:
            pygame.quit()  # Close Pygame
            subprocess.run(["taskkill", "/f", "/im", "ffmpeg-win64-v4.2.2.exe"], stderr=subprocess.DEVNULL)
        except Exception:
            pass


if __name__ == "__main__":
    # setx api_key "api-key" pour crée variable d'environement
    api_key = "AIzaSyBnrifjZ0vneVjtV2vfLx3y7uWocMmEIrs"
    app = LecteurMusiqueApp(api_key)

    # répertoire de travail
    musique_directory = os.path.join(os.path.dirname(__file__), "musique")
    os.chdir(musique_directory)

    app.mainloop()
