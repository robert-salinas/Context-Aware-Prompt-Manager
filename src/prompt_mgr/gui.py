import customtkinter as ctk
import json
import os
import pyperclip
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from .manager import PromptManager

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
    def __init__(self):
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
        
        # Inicializar Backend
        self.mgr = PromptManager(os.getcwd())
        if not os.path.exists(os.path.join(os.getcwd(), "prompts")):
            self.mgr.init_project()

        self.config_data = self.load_config()
        self.db_path = self.config_data.get("db_path", "prompts.json")
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
        """Carga los prompts desde el backend."""
        try:
            backend_prompts = self.mgr.list_prompts()
            gui_prompts = []
            for bp in backend_prompts:
                gui_prompts.append({
                    "id": bp.get("filename", ""),
                    "title": bp.get("name", "Sin título"),
                    "category": bp.get("tags", ["Otros"])[0] if bp.get("tags") else "Otros",
                    "tags": bp.get("tags", []),
                    "content": bp.get("template", ""),
                    "updated_at": ""
                })
            return gui_prompts
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return []

    def save_data(self):
        """No se usa con el nuevo backend."""
        pass

    def setup_ui(self):
        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # 1. Header (Title, Subtitle)
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_group.grid(row=0, column=0, sticky="w")
        
        self.main_title = ctk.CTkLabel(self.title_group, text="Prompt Manager", 
                                      font=ctk.CTkFont(size=32, weight="bold"), text_color=RS_ORANGE)
        self.main_title.pack(anchor="w")
        
        self.sub_title = ctk.CTkLabel(self.title_group, text="By Robert Salinas", 
                                     font=ctk.CTkFont(size=14), text_color=RS_TEXT_MUTED)
        self.sub_title.pack(anchor="w")

        # 2. Tabview
        self.tab_view = ctk.CTkTabview(self.main_container, fg_color=RS_DARK_BG)
        self.tab_view.grid(row=1, column=0, sticky="nsew")
        
        self.tab_view.add("Catálogo 📂")
        self.tab_view.add("Contexto 🧠")
        self.tab_view.add("Configuración ⚙️")

        self.setup_catalogo_tab()
        self.setup_contexto_tab()
        self.setup_config_tab()

        # 5. Editor View (Hidden by default)
        self.editor_view = ctk.CTkFrame(self.main_container, fg_color=RS_DARK_BG, corner_radius=0)

        self.refresh_list()

    def setup_catalogo_tab(self):
        tab = self.tab_view.tab("Catálogo 📂")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        # KPI Cards
        self.kpi_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_kpi_card(0, "Estado", "Activo", "status")
        self.create_kpi_card(1, "Total Prompts", "0", "prompts_count")
        self.create_kpi_card(2, "Categoría Top", "N/A", "top_category")
        self.create_kpi_card(3, "Última Act.", "Hoy", "last_update")
        self.update_kpis()

        # Controls
        self.controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
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

        # Prompts List
        self.scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color=RS_DARK_CARD, 
                                                     label_text="Catálogo de Prompts", label_text_color=RS_ORANGE,
                                                     corner_radius=12)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def setup_contexto_tab(self):
        tab = self.tab_view.tab("Contexto 🧠")
        tab.grid_columnconfigure(0, weight=1)
        
        self.context_info = ctk.CTkTextbox(tab, fg_color=RS_DARK_CARD, text_color=RS_TEXT_WHITE, font=ctk.CTkFont(size=14))
        self.context_info.pack(fill="both", expand=True, padx=20, pady=20)
        
        btn = ctk.CTkButton(tab, text="Actualizar Contexto", fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK, command=self.update_context_view)
        btn.pack(pady=10)
        
        self.update_context_view()

    def update_context_view(self):
        try:
            ctx = self.mgr.analyzer.analyze()
            text = f"📂 Proyecto: {ctx.get('project_name')}\n\n"
            text += f"🛠️ Tech Stack: {', '.join(ctx.get('tech_stack', []))}\n"
            text += f"🌐 Lenguajes: {', '.join(ctx.get('languages', []))}\n"
            text += f"🧪 Tests: {'Sí' if ctx.get('has_tests') else 'No'}\n"
            text += f"📖 README: {'Sí' if ctx.get('has_readme') else 'No'}\n\n"
            text += "--- Resumen README ---\n"
            text += ctx.get("readme_summary", "N/A")
            
            self.context_info.configure(state="normal")
            self.context_info.delete("1.0", "end")
            self.context_info.insert("1.0", text)
            self.context_info.configure(state="disabled")
        except Exception as e:
            print(f"Error actualizando contexto: {e}")

    def setup_config_tab(self):
        tab = self.tab_view.tab("Configuración ⚙️")
        tab.grid_columnconfigure(0, weight=1)
        
        # Panel Estilo Card para Configs
        panel = ctk.CTkFrame(tab, fg_color=RS_DARK_CARD, corner_radius=12)
        panel.pack(fill="both", expand=True, padx=20, pady=20)
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        self.create_config_item(content, "Ruta Base de Datos", self.config_data.get("db_path", "prompts.json"), "db_path")
        self.create_config_item(content, "Categoría Predeterminada", self.config_data.get("default_cat", "Ingeniería"), "default_cat", is_option=True)
        self.create_config_item(content, "Filtro de Seguridad", self.config_data.get("forbidden", "admin, root"), "forbidden")

        ctk.CTkButton(content, text="Guardar Configuración", fg_color=RS_ORANGE, command=self.on_save_config).pack(pady=20)

    def create_kpi_card(self, col: int, title: str, value: str, attr_name: str):
        card = ctk.CTkFrame(self.kpi_frame, fg_color=RS_DARK_CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color=RS_TEXT_MUTED)
        title_label.pack(pady=(15, 0))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=RS_ORANGE)
        value_label.pack(pady=(0, 15))
        setattr(self, f"kpi_{attr_name}", value_label)

    def show_main(self):
        self.editor_view.grid_forget()
        self.tab_view.grid(row=1, column=0, sticky="nsew")

    def open_editor(self, prompt: Optional[Dict[str, Any]] = None):
        """Abre el editor en la ventana actual."""
        self.tab_view.grid_forget()
        self.editor_view.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
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
        title = self.title_entry.get()
        category = self.category_opt.get()
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        if category not in tags:
            tags.insert(0, category) # El primer tag es la categoría
        content = self.content_text.get("1.0", "end-1c")

        backend_data = {
            "name": title,
            "description": f"Categoría: {category}",
            "template": content,
            "tags": tags,
            "version": "1.0.0"
        }

        filename = self.editing_prompt_id if self.editing_prompt_id else f"{title.lower().replace(' ', '_')}.yaml"
        if not filename.endswith(".yaml"):
            filename += ".yaml"

        try:
            self.mgr.add_prompt(filename, backend_data)
            self.show_toast(f"Prompt '{title}' guardado")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo guardar el prompt: {e}")

        # Recargar datos
        self.prompts_data = self.load_data()
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

    def show_toast(self, message: str, duration: int = 2500):
        """Muestra una notificación flotante no bloqueante."""
        toast_frame = ctk.CTkFrame(self, fg_color=RS_ORANGE, corner_radius=20)
        toast_frame.place(relx=0.5, rely=0.9, anchor="center")
        
        label = ctk.CTkLabel(toast_frame, text=message, font=ctk.CTkFont(size=13, weight="bold"), text_color=RS_DARK_BG)
        label.pack(padx=20, pady=8)
        
        # Eliminar el widget después del tiempo indicado
        self.after(duration, toast_frame.destroy)

    def on_search(self, event=None):
        self.refresh_list()

    def refresh_list(self, query: str = None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().lower() if not query else query.lower()
        
        if query:
            try:
                search_results = self.mgr.search_prompts(query)
                filtered = []
                for sr in search_results:
                    filtered.append({
                        "id": sr.get("path", ""),
                        "title": sr.get("name", ""),
                        "category": sr.get("tags", ["Otros"])[0] if sr.get("tags") else "Otros",
                        "tags": sr.get("tags", []),
                        "content": sr.get("content", ""),
                        "updated_at": ""
                    })
            except Exception as e:
                print(f"Error en búsqueda FTS: {e}")
                filtered = []
        else:
            # Recargar de la lista general
            self.prompts_data = self.load_data()
            filtered = self.prompts_data

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
        # Tags a modo de "Pills"
        tags_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        tags_frame.pack(anchor="w", pady=(5, 0))
        
        for tag in prompt.get("tags", []):
            # Usar color de tarjeta para el fondo de la píldora
            pill = ctk.CTkFrame(tags_frame, fg_color=RS_DARK_CARD, corner_radius=15, border_width=1, border_color=RS_ORANGE)
            pill.pack(side="left", padx=2)
            ctk.CTkLabel(pill, text=tag, font=ctk.CTkFont(size=10), text_color=RS_TEXT_WHITE, padx=8, pady=1).pack()

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
        # Buscar variables estilo Jinja2: {{ variable }}
        variables = re.findall(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", content)
        if variables:
            var_dialog = RS_VariableDialog(self, list(set(variables)), content, self.final_copy)
            var_dialog.grab_set()
        else:
            self.final_copy(content)

    def final_copy(self, text: str):
        pyperclip.copy(text)
        self.show_toast("¡Copiado al portapapeles!")

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
            ctk.CTkLabel(container, text=f"{{{{ {var} }}}}:", text_color=RS_TEXT_WHITE).pack(anchor="w")
            entry = ctk.CTkEntry(container, fg_color=RS_DARK_CARD, border_color=RS_ORANGE, text_color=RS_TEXT_WHITE)
            entry.pack(fill="x", pady=(5, 15))
            self.entries[var] = entry
        ctk.CTkButton(container, text="PROCESAR Y COPIAR", fg_color=RS_ORANGE, hover_color=RS_ORANGE_DARK, height=45,
                    command=self.on_process).pack(pady=20, fill="x")

    def on_process(self):
        final_text = self.content
        for var, entry in self.entries.items():
            val = entry.get() or f"{{{{ {var} }}}}"
            pattern = r"\{\{\s*" + var + r"\s*\}\}"
            final_text = re.sub(pattern, val, final_text)
        self.callback(final_text)
        self.destroy()

if __name__ == "__main__":
    app = RSPromptManagerGUI()
    app.mainloop()
