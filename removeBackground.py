import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

executor = ThreadPoolExecutor(max_workers=1)

def process_video(video_path, final_output_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(final_output_path, fourcc, fps, (frame_width, frame_height))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_bar["maximum"] = total_frames

    background_color = (0, 0, 0)
    current_frame = 0

    log_text.insert(tk.END, "Iniciando o processamento do vídeo...\n")
    log_text.update_idletasks()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = selfie_segmentation.process(rgb_frame)

        mask = results.segmentation_mask
        condition = mask > 0.5
        mask = (condition * 255).astype(np.uint8)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.erode(mask, kernel, iterations=2)

        output_frame = frame.copy()
        output_frame[mask == 0] = background_color
        out.write(output_frame)

        current_frame += 1
        progress_bar["value"] = current_frame
        root.update_idletasks()

        log_text.insert(tk.END, f"Processando frame {current_frame} de {total_frames}...\n")
        log_text.see(tk.END)
        log_text.update_idletasks()

    cap.release()
    out.release()

    log_text.insert(tk.END, "Processamento de vídeo concluído!\n")
    log_text.update_idletasks()

    messagebox.showinfo("Sucesso", f"Vídeo salvo sem áudio em: {final_output_path}")

def start_processing():
    video_path = filedialog.askopenfilename(title="Selecione o vídeo", filetypes=[("MP4 files", "*.mp4")])
    if not video_path:
        messagebox.showwarning("Atenção", "Nenhum vídeo selecionado.")
        return

    final_output_path = "FundoRemovido.mp4"
    executor.submit(process_video, video_path, final_output_path)

root = tk.Tk()
root.title("Remove Background")
root.geometry("500x500")
root.configure(bg="#1e1e1e")

try:
    icon_path = resource_path("remover.png") 
    icon_image = ImageTk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image) 
except Exception as e:
    print(f"Erro ao carregar o ícone: {e}")

title_label = tk.Label(root, text="Remove Background", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e")
title_label.pack(pady=(5, 5))

description_label = tk.Label(root, text="Clique no botão para selecionar o vídeo a remover o fundo", font=("Arial", 12), fg="gray", bg="#1e1e1e")
description_label.pack(pady=5)

progress_label = tk.Label(root, text="Progresso", font=("Arial", 12), fg="white", bg="#1e1e1e")
progress_label.pack(pady=(15, 0))

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

process_button = tk.Button(root, text="Selecionar e Remover Fundo", command=start_processing, font=("Arial", 14), bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5)
process_button.pack(pady=20)

log_text = tk.Text(root, height=10, width=58, wrap="word", bg="#1e1e1e", fg="white", font=("Arial", 10))
log_text.pack(pady=(10, 10))
log_text.insert(tk.END, "Log de Processamento:\n")

root.mainloop()
