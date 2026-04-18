from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple

import cv2
from PIL import Image, ImageTk

from backend.image_processing import create_simple_mosaic, load_images_from_folder, save_image
from backend.model3d import generate_simple_3d_model
from backend.models import ClientData
from backend.pdf_report import generate_pdf_report
from backend.terrain_analysis import full_analysis

Point = Tuple[int, int]


class RuralAnalyzerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Bar-o | Análise Rural por Drone")
        self.root.geometry("1200x750")

        self.images_folder = ""
        self.mosaic = None
        self.mosaic_path = ""
        self.points: List[Point] = []
        self.tk_image = None

        self._build_ui()

    def _build_ui(self) -> None:
        frame_left = tk.Frame(self.root, padx=10, pady=10)
        frame_left.pack(side=tk.LEFT, fill=tk.Y)
        frame_right = tk.Frame(self.root, padx=10, pady=10)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(frame_left, text="Cadastro do Cliente", font=("Arial", 12, "bold")).pack(anchor="w")

        self.nome_cliente = self._entry(frame_left, "Nome do cliente")
        self.nome_prop = self._entry(frame_left, "Nome da propriedade")
        self.cidade = self._entry(frame_left, "Cidade")
        self.data = self._entry(frame_left, "Data (dd/mm/aaaa)")

        tk.Label(frame_left, text="Observações").pack(anchor="w")
        self.obs = tk.Text(frame_left, height=4, width=35)
        self.obs.pack(anchor="w", pady=(0, 10))

        tk.Button(frame_left, text="1) Selecionar pasta de imagens", command=self.select_images_folder).pack(fill=tk.X, pady=3)
        tk.Button(frame_left, text="2) Gerar mapa (ortomosaico)", command=self.generate_mosaic).pack(fill=tk.X, pady=3)
        tk.Button(frame_left, text="3) Limpar pontos do polígono", command=self.clear_points).pack(fill=tk.X, pady=3)
        tk.Button(frame_left, text="4) Gerar relatório PDF", command=self.generate_report).pack(fill=tk.X, pady=3)
        tk.Button(frame_left, text="5) Premium: gerar modelo 3D", command=self.generate_3d).pack(fill=tk.X, pady=3)

        self.status = tk.StringVar(value="Pronto. Selecione as imagens de drone.")
        tk.Label(frame_left, textvariable=self.status, wraplength=280, fg="blue").pack(anchor="w", pady=(10, 0))

        tk.Label(frame_right, text="Mapa do terreno (clique para desenhar limites)", font=("Arial", 11, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(frame_right, bg="#f2f2f2", width=850, height=680)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def _entry(self, parent: tk.Widget, label: str) -> tk.Entry:
        tk.Label(parent, text=label).pack(anchor="w")
        entry = tk.Entry(parent, width=35)
        entry.pack(anchor="w", pady=(0, 7))
        return entry

    def select_images_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecione pasta com imagens")
        if folder:
            self.images_folder = folder
            self.status.set(f"Pasta selecionada: {folder}")

    def generate_mosaic(self) -> None:
        try:
            images = load_images_from_folder(self.images_folder)
            self.mosaic = create_simple_mosaic(images)
            self.mosaic_path = save_image(self.mosaic, os.path.join("output", "mosaic.png"))
            self._show_image(self.mosaic)
            self.status.set("Mapa gerado com sucesso. Agora marque os pontos do limite.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def _show_image(self, bgr_img) -> None:
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        canvas_w = self.canvas.winfo_width() or 850
        canvas_h = self.canvas.winfo_height() or 680
        scale = min(canvas_w / w, canvas_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(rgb, (new_w, new_h))

        pil_img = Image.fromarray(resized)
        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_canvas_click(self, event) -> None:
        if self.mosaic is None:
            return
        point = (event.x, event.y)
        self.points.append(point)
        self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill="red")
        if len(self.points) > 1:
            p1 = self.points[-2]
            p2 = self.points[-1]
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="yellow", width=2)
        if len(self.points) > 2:
            p0 = self.points[0]
            pn = self.points[-1]
            self.canvas.delete("closure")
            self.canvas.create_line(pn[0], pn[1], p0[0], p0[1], fill="orange", dash=(4, 2), tags="closure")

    def clear_points(self) -> None:
        self.points.clear()
        if self.mosaic is not None:
            self._show_image(self.mosaic)
        self.status.set("Pontos limpos. Redesenhe o limite do terreno.")

    def _collect_client_data(self) -> ClientData:
        return ClientData(
            nome_cliente=self.nome_cliente.get().strip() or "Não informado",
            nome_propriedade=self.nome_prop.get().strip() or "Não informado",
            cidade=self.cidade.get().strip() or "Não informado",
            data=self.data.get().strip() or "Não informado",
            observacoes=self.obs.get("1.0", tk.END).strip(),
        )

    def generate_report(self) -> None:
        if self.mosaic is None:
            messagebox.showwarning("Aviso", "Gere o mapa antes de criar o relatório.")
            return
        if len(self.points) < 3:
            messagebox.showwarning("Aviso", "Marque ao menos 3 pontos para formar o polígono.")
            return

        client = self._collect_client_data()
        analysis = full_analysis(self.mosaic, self.points, "output")
        pdf_path = os.path.join("output", "relatorio_terreno.pdf")
        generate_pdf_report(pdf_path, client, analysis, self.mosaic_path)

        self.status.set(f"Relatório gerado: {pdf_path}")
        messagebox.showinfo("Sucesso", f"Relatório criado em: {pdf_path}")

    def generate_3d(self) -> None:
        if not self.mosaic_path:
            messagebox.showwarning("Aviso", "Gere o mapa antes do modelo 3D.")
            return
        try:
            model_path = generate_simple_3d_model(self.mosaic_path, "models_3d")
            self.status.set(f"Modelo 3D gerado: {model_path}")
            messagebox.showinfo("Premium", f"Modelo 3D exportado: {model_path}")
        except Exception as exc:
            messagebox.showerror("Erro 3D", str(exc))
