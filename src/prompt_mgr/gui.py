import customtkinter as ctk
import json
import os
import pyperclip
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# RS Standard - Design System
RS_ORANGE = "#FF7A3D"
RS_ORANGE_DARK = "#E86A2A"
RS_DARK_BG = "#1A1F2E"
RS_DARK_CARD = "#2D3142"
RS_TEXT_WHITE = "#FFFFFF"
RS_TEXT_MUTED = "#9CA3AF"

class RSPromptManagerGUI(ctk.CTk):
    """
    RS Prompt Manager - Desktop Application
    Protocolo RS Standard | UI Re-designed (No Sidebar)
    """
    def __init__(self, db_path: str = "prompts.json"):
        super().__init__()

        # Configuración de Ventana
        self.title("RS Prompt Manager v1.0.0")
        self.geometry("1000x800")
        self.configure(fg_color=RS_DARK_BG)
        
        # Cargar Icono si existe
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        
        self.db_path = db_path
        self.config_data = self.load_config()
        self.db_path = self.config_data.get("db_path", db_path)
        self.prompts_data: List[Dict[str, Any]] = self.load_data()
        self.current_category = "Todos"
        self.editing_prompt_id = None
        
        # Diccionario para guardar referencias de widgets de config
        self.config_widgets = {}

        # Grid Layout (1x1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración de la aplicación."""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"db_path": "prompts.json", "default_cat": "Ingeniería", "forbidden": "admin, root, password"}

    def save_config(self, config_data: Dict[str, Any]):
        """Guarda la configuración de la aplicación."""
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

    def load_data(self) -> List[Dict[str, Any]]:
        """Carga la base de datos de prompts local."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_data(self):
        """Guarda la base de datos de prompts local."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.prompts_data, f, indent=4, ensure_ascii=False)

    def setup_ui(self):
        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(3, weight=1)

        # 1. Header (Title, Subtitle, Config Button)
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Título y Subtítulo
        self.title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_group.grid(row=0, column=0, sticky="w")
        
        self.main_title = ctk.CTkLabel(self.title_group, text="Prompt Manager", 
                                      font=ctk.CTkFont(size=32, weight="bold"), text_color=RS_ORANGE)
        self.main_title.pack(anchor="w")
        
        self.sub_title = ctk.CTkLabel(self.title_group, text="By Robert Salinas", 
                                     font=ctk.CTkFont(size=14), text_color=RS_TEXT_MUTED)
        self.sub_title.pack(anchor="w")

        # Botón Configuración (Estilo Icono + Texto)
        self.config_btn = ctk.CTkButton(self.header_frame, text="⚙️ Configuración", 
                                      fg_color=RS_DARK_CARD, hover_color=RS_ORANGE,
                                      width=120, height=35, corner_radius=8,
                                      command=self.show_config)
        self.config_btn.grid(row=0, column=1, sticky="e")

        # 2. KPI Cards
        self.kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_kpi_card(0, "Estado", "Activo", "status")
        self.create_kpi_card(1, "Total Prompts", "0", "prompts_count")
        self.create_kpi_card(2, "Categoría Top", "N/A", "top_category")
        self.create_kpi_card(3, "Última Act.", "Hoy", "last_update")
        self.update_kpis()

        # 3. Controls (Search & Add)
        self.controls_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.controls_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Buscar por título o etiquetas...", 
                                      fg_color=RS_DARK_CARD, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE,
                                      height=40)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.add_btn = ctk.CTkButton(self.controls_frame, text="NUEVO PROMPT", fg_color=RS_ORANGE, 
                                   hover_color=RS_ORANGE_DARK, font=ctk.CTkFont(weight="bold"),
                                   width=150, height=40,
                                   command=self.open_editor)
        self.add_btn.grid(row=0, column=1)

        # 4. Prompts List
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_container, fg_color=RS_DARK_CARD, 
                                                     label_text="Catálogo de Prompts", label_text_color=RS_ORANGE,
                                                     corner_radius=12)
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # 5. Editor View (Hidden by default)
        self.editor_view = ctk.CTkFrame(self.main_container, fg_color=RS_DARK_BG, corner_radius=0)
        # grid will be called in open_editor

        # Config View (Hidden)
        self.config_view = ctk.CTkFrame(self.main_container, fg_color=RS_DARK_BG, corner_radius=0)
        # show_config will grid it

        self.refresh_list()

    def create_kpi_card(self, col: int, title: str, value: str, attr_name: str):
        card = ctk.CTkFrame(self.kpi_frame, fg_color=RS_DARK_CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color=RS_TEXT_MUTED)
        title_label.pack(pady=(15, 0))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=RS_ORANGE)
        value_label.pack(pady=(0, 15))
        setattr(self, f"kpi_{attr_name}", value_label)

    def show_main(self):
        self.config_view.grid_forget()
        self.editor_view.grid_forget()
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew")

    def open_editor(self, prompt: Optional[Dict[str, Any]] = None):
        """Abre el editor en la ventana actual."""
        self.header_frame.grid_forget()
        self.kpi_frame.grid_forget()
        self.controls_frame.grid_forget()
        self.scrollable_frame.grid_forget()
        self.config_view.grid_forget()
        
        self.editor_view.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        for widget in self.editor_view.winfo_children():
            widget.destroy()

        self.editing_prompt_id = prompt.get("id") if prompt else None
        
        # Título del Editor
        title_text = "Editar Prompt" if prompt else "Nuevo Prompt"
        ctk.CTkLabel(self.editor_view, text=title_text, 
                    font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0, 20))

        # Panel Estilo Card para el Editor
        panel = ctk.CTkFrame(self.editor_view, fg_color=RS_DARK_CARD, corner_radius=12)
        panel.pack(fill="both", expand=True, padx=2, pady=2)
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=40)

        # Campos del Editor
        ctk.CTkLabel(content, text="Título del Prompt:", text_color=RS_ORANGE, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(content, fg_color=RS_DARK_BG, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE, height=35)
        self.title_entry.pack(fill="x", pady=(5, 15))
        if prompt: self.title_entry.insert(0, prompt["title"])

        ctk.CTkLabel(content, text="Categoría:", text_color=RS_ORANGE, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.category_opt = ctk.CTkOptionMenu(content, values=["Ingeniería", "Python", "Branding", "IA Persona", "Otros"],
                                            fg_color=RS_DARK_BG, button_color=RS_ORANGE, dropdown_fg_color=RS_DARK_CARD,
                                            width=400)
        self.category_opt.pack(anchor="w", pady=(5, 15))
        if prompt: self.category_opt.set(prompt.get("category", "Otros"))
        else: self.category_opt.set(self.config_data.get("default_cat", "Ingeniería"))

        ctk.CTkLabel(content, text="Etiquetas (separadas por coma):", text_color=RS_ORANGE, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.tags_entry = ctk.CTkEntry(content, fg_color=RS_DARK_BG, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE, height=35)
        self.tags_entry.pack(fill="x", pady=(5, 15))
        if prompt: self.tags_entry.insert(0, ", ".join(prompt.get("tags", [])))

        ctk.CTkLabel(content, text="Contenido (Usa [VARIABLE]):", text_color=RS_ORANGE, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.content_text = ctk.CTkTextbox(content, fg_color=RS_DARK_BG, border_width=1, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE)
        self.content_text.pack(fill="both", expand=True, pady=(5, 20))
        if prompt: self.content_text.insert("1.0", prompt["content"])

        # Buttons Guardar/Cancelar
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Guardar Prompt", fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK,
                    width=150, height=40, command=self.on_save_prompt).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="transparent", border_width=1, border_color=RS_ORANGE,
                    width=150, height=40, command=self.show_main).pack(side="left", padx=10)

    def on_save_prompt(self):
        """Guarda los datos del editor y vuelve a la vista principal."""
        data = {
            "title": self.title_entry.get(),
            "category": self.category_opt.get(),
            "tags": [t.strip() for t in self.tags_entry.get().split(",") if t.strip()],
            "content": self.content_text.get("1.0", "end-1c"),
            "updated_at": datetime.now().isoformat()
        }
        
        if self.editing_prompt_id:
            data["id"] = self.editing_prompt_id
            for i, p in enumerate(self.prompts_data):
                if p.get("id") == self.editing_prompt_id:
                    self.prompts_data[i] = data
                    break
        else:
            data["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
            self.prompts_data.append(data)
        
        self.save_data()
        self.update_kpis()
        self.refresh_list()
        self.show_main()

    def show_config(self):
        self.header_frame.grid_forget()
        self.kpi_frame.grid_forget()
        self.controls_frame.grid_forget()
        self.scrollable_frame.grid_forget()
        self.editor_view.grid_forget()
        
        self.config_view.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        for widget in self.config_view.winfo_children():
            widget.destroy()
            
        self.config_widgets = {} # Limpiar referencias previas

        # Título Configuración
        ctk.CTkLabel(self.config_view, text="Configuración del Sistema", 
                    font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0, 20))
        
        # Panel Estilo Card para Configs
        panel = ctk.CTkFrame(self.config_view, fg_color=RS_DARK_CARD, corner_radius=12)
        panel.pack(fill="both", expand=True, padx=2, pady=2)
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Config Items (Estilo foto de referencia)
        self.create_config_item(content, "Ruta Base de Datos", self.config_data.get("db_path", "prompts.json"), "db_path")
        self.create_config_item(content, "Categoría Predeterminada", self.config_data.get("default_cat", "Ingeniería"), "default_cat", is_option=True)
        self.create_config_item(content, "Filtro de Seguridad (Palabras prohibidas)", self.config_data.get("forbidden", "admin, root, password"), "forbidden")

        # Buttons Guardar/Cancelar
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=40)
        
        ctk.CTkButton(btn_frame, text="Guardar y Volver", fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK,
                    width=150, height=40, command=self.on_save_config).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="transparent", border_width=1, border_color=RS_ORANGE,
                    width=150, height=40, command=self.show_main).pack(side="left", padx=10)

        # Footer
        footer = ctk.CTkLabel(self.config_view, text="RS Digital\nby Robert Salinas", 
                             font=ctk.CTkFont(size=10), text_color=RS_TEXT_MUTED)
        footer.pack(side="bottom", pady=20)

    def on_save_config(self):
        """Recopila los valores de los widgets y guarda la configuración."""
        new_config = {}
        for attr_name, widget in self.config_widgets.items():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkOptionMenu)):
                new_config[attr_name] = widget.get()
            elif isinstance(widget, ctk.CTkTextbox):
                new_config[attr_name] = widget.get("1.0", "end-1c")
        
        self.config_data.update(new_config)
        self.save_config(self.config_data)
        
        # Si cambió la ruta de la DB, recargar datos
        if self.db_path != self.config_data.get("db_path"):
            self.db_path = self.config_data.get("db_path")
            self.prompts_data = self.load_data()
            self.refresh_list()
            self.update_kpis()
            
        self.show_main()

    def create_config_item(self, parent, label, value, attr_name, is_option=False):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(item_frame, text=label, text_color=RS_TEXT_WHITE, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        if is_option:
            opt = ctk.CTkOptionMenu(item_frame, values=["Ingeniería", "Python", "Branding", "IA Persona", "Otros"],
                                   fg_color=RS_DARK_BG, button_color=RS_ORANGE, dropdown_fg_color=RS_DARK_CARD,
                                   width=400)
            opt.set(value)
            opt.pack(anchor="w", pady=(5, 0))
            self.config_widgets[attr_name] = opt
        else:
            entry_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            entry_frame.pack(fill="x", pady=(5, 0))
            
            entry = ctk.CTkEntry(entry_frame, fg_color=RS_DARK_BG, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE,
                                width=400, height=35)
            entry.pack(side="left")
            entry.insert(0, value)
            self.config_widgets[attr_name] = entry
            
            if "Ruta" in label:
                ctk.CTkButton(entry_frame, text="...", width=40, height=35, fg_color="#3B82F6",
                            command=self.browse_db_file).pack(side="left", padx=10)

    def browse_db_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(defaultextension=".json", 
                                             filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if filename:
            # Buscar el widget de db_path y actualizarlo
            if "db_path" in self.config_widgets:
                self.config_widgets["db_path"].delete(0, "end")
                self.config_widgets["db_path"].insert(0, filename)

    def update_kpis(self):
        total = len(self.prompts_data)
        self.kpi_prompts_count.configure(text=str(total))
        
        if total > 0:
            cats = [p.get("category", "Otros") for p in self.prompts_data]
            top_cat = max(set(cats), key=cats.count)
            self.kpi_top_category.configure(text=top_cat)
            
            dates = [p.get("updated_at", "") for p in self.prompts_data if p.get("updated_at")]
            if dates:
                last = max(dates).split("T")[0]
                self.kpi_last_update.configure(text=last)
        else:
            self.kpi_top_category.configure(text="N/A")
            self.kpi_last_update.configure(text="Hoy")

    def on_search(self, event=None):
        self.refresh_list()

    def refresh_list(self, query: str = None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().lower() if not query else query.lower()
        filtered = self.prompts_data
        
        if query:
            filtered = [p for p in filtered if query in p["title"].lower() or any(query in t.lower() for t in p.get("tags", []))]

        for i, prompt in enumerate(filtered):
            self.create_prompt_item(prompt, i)

    def create_prompt_item(self, prompt: Dict[str, Any], index: int):
        item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=RS_DARK_BG, corner_radius=12)
        item_frame.grid(row=index, column=0, sticky="ew", pady=8, padx=10)
        item_frame.grid_columnconfigure(1, weight=1)

        # Title/Tags
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        ctk.CTkLabel(info_frame, text=prompt["title"], font=ctk.CTkFont(size=16, weight="bold"), text_color=RS_ORANGE).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=" | ".join(prompt.get("tags", [])), font=ctk.CTkFont(size=11), text_color=RS_TEXT_MUTED).pack(anchor="w")

        # Preview
        preview = prompt["content"][:100] + "..." if len(prompt["content"]) > 100 else prompt["content"]
        ctk.CTkLabel(item_frame, text=preview, font=ctk.CTkFont(slant="italic"), text_color=RS_TEXT_WHITE, wraplength=400).grid(row=0, column=1, padx=20)

        # Buttons
        btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=20)

        ctk.CTkButton(btn_frame, text="COPIAR", width=90, fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK,
                    command=lambda p=prompt: self.copy_to_clipboard(p["content"])).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="EDITAR", width=90, fg_color="gray30", hover_color="gray40",
                    command=lambda p=prompt: self.open_editor(p)).pack(side="left", padx=5)

    def copy_to_clipboard(self, content: str):
        variables = re.findall(r"\[([A-Z0-9_]+)\]", content)
        if variables:
            var_dialog = RS_VariableDialog(self, list(set(variables)), content, self.final_copy)
            var_dialog.grab_set()
        else:
            self.final_copy(content)

    def final_copy(self, text: str):
        pyperclip.copy(text)
        print("Copiado al portapapeles")

class RS_VariableDialog(ctk.CTkToplevel):
    def __init__(self, parent, variables: List[str], content: str, callback):
        super().__init__(parent)
        self.title("Sustituir Variables RS")
        self.geometry("400x500")
        self.configure(fg_color=RS_DARK_BG)
        self.variables = variables
        self.content = content
        self.callback = callback
        self.entries = {}
        self.setup_ui()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(container, text="Personalizar Variables", font=ctk.CTkFont(size=20, weight="bold"), text_color=RS_ORANGE).pack(pady=(0, 20))
        for var in self.variables:
            ctk.CTkLabel(container, text=f"[{var}]:", text_color=RS_TEXT_WHITE).pack(anchor="w")
            entry = ctk.CTkEntry(container, fg_color=RS_DARK_CARD, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE)
            entry.pack(fill="x", pady=(5, 15))
            self.entries[var] = entry
        ctk.CTkButton(container, text="PROCESAR Y COPIAR", fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK, height=45,
                    command=self.on_process).pack(pady=20, fill="x")

    def on_process(self):
        final_text = self.content
        for var, entry in self.entries.items():
            val = entry.get() or f"[{var}]"
            final_text = final_text.replace(f"[{var}]", val)
        self.callback(final_text)
        self.destroy()

if __name__ == "__main__":
    app = RSPromptManagerGUI()
    app.mainloop()
