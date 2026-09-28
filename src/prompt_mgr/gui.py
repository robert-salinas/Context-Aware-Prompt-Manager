"""Compact RS desktop interface for contextual prompt workflows."""

import ctypes
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

import prompt_mgr
from prompt_mgr.manager import PromptManager
from prompt_mgr.settings import SettingsStore

ORANGE = ("#FF7A3D", "#FF7A3D")
ORANGE_HOVER = ("#D65A1A", "#E86A2A")
BG = ("#F3F5F8", "#131923")
SURFACE = ("#FFFFFF", "#202735")
INPUT = ("#EDF0F5", "#171E2A")
BORDER = ("#CBD2DE", "#354154")
TEXT = ("#111827", "#FFFFFF")
MUTED = ("#4B5563", "#BAC4D2")
SUCCESS = ("#059669", "#10B981")
ERROR = ("#DC2626", "#EF4444")
FONT = "Segoe UI"
TITLE_FONT = "Bahnschrift"


def resource_root():
    return Path(
        getattr(sys, "_MEIPASS", Path(prompt_mgr.__file__).resolve().parents[2])
    )


def ui_button(parent, text, command, primary=False, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=7,
        border_width=1,
        border_color=ORANGE if primary else BORDER,
        fg_color=ORANGE if primary else "transparent",
        hover_color=ORANGE_HOVER,
        text_color="#181C25" if primary else TEXT,
        font=(FONT, 12, "bold"),
        **kwargs,
    )


def ui_entry(parent, **kwargs):
    return ctk.CTkEntry(
        parent,
        height=34,
        corner_radius=7,
        border_width=1,
        border_color=BORDER,
        fg_color=INPUT,
        text_color=TEXT,
        font=(FONT, 12),
        **kwargs,
    )


class RSPromptManagerGUI(ctk.CTk):
    def __init__(self):
        self.store = SettingsStore()
        ctk.set_appearance_mode(self.store.settings.theme)
        ctk.set_widget_scaling(self.store.settings.ui_scale / 100)
        super().__init__()
        self.title("RS Context Prompt Manager")
        self.geometry("1180x760+24+24")
        self.minsize(1000, 640)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._set_native_icon()
        bundled = resource_root() / "prompts"
        library = self.store.prepare_library(bundled)
        active = Path(self.store.settings.active_project).expanduser()
        if not active.is_dir():
            active = Path.cwd()
        self.manager = PromptManager(
            str(active), str(library), auto_version=self.store.settings.auto_version
        )
        self.manager.init_project(seed_sample=False)
        self.selected_filename = None
        self.variable_entries = {}
        self.session_drafts = {}
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.context_future = None
        self.prompt_buttons = []
        self._build_header()
        self._build_project_bar()
        self._build_workspace()
        self._build_footer()
        self.protocol("WM_DELETE_WINDOW", self._close_app)
        self.refresh_context()
        self.bind_all("<Control-f>", lambda _event: self.search_entry.focus_set())
        self.bind_all("<Control-n>", lambda _event: self.open_editor())
        self.bind_all("<Control-Return>", lambda _event: self.copy_contextual())

    def _set_native_icon(self):
        icon = resource_root() / "assets" / "icon.ico"
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "RS.Digital.ContextPromptManager"
            )
            self.iconbitmap(default=str(icon))
            self.after(200, lambda: self.iconbitmap(default=str(icon)))
        except (AttributeError, OSError, tk.TclError):
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(14, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="RS DIGITAL  /  CREATOR TOOLS",
            font=(FONT, 9, "bold"),
            text_color=ORANGE,
        ).grid(row=0, column=0, sticky="w")
        title = ctk.CTkFrame(header, fg_color="transparent")
        title.grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(
            title, text="Context", font=(TITLE_FONT, 27, "bold"), text_color=TEXT
        ).pack(side="left")
        self.accent_title = ctk.CTkLabel(
            title,
            text=" Prompt Manager",
            font=(TITLE_FONT, 27, "bold"),
            text_color=ORANGE,
        )
        self.accent_title.pack(side="left")
        ctk.CTkLabel(
            header,
            text="Biblioteca local · contexto visible · control del usuario",
            font=(FONT, 12),
            text_color=MUTED,
        ).grid(row=2, column=0, sticky="w")
        self.settings_btn = ui_button(
            header, "⚙  Preferencias", self.open_settings, width=116
        )
        self.settings_btn.grid(row=0, column=1, rowspan=3)
        self.header_accent = ctk.CTkFrame(header, width=0, height=2, fg_color=ORANGE)
        self.header_accent.grid(row=3, column=0, sticky="w", pady=(7, 0))
        ctk.CTkFrame(header, height=1, fg_color=BORDER).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(7, 0)
        )
        self._animate_header()

    def _animate_header(self, step=0):
        widths = (20, 44, 72, 100, 130)
        if step < len(widths):
            self.header_accent.configure(width=widths[step])
            self.after(45, lambda: self._animate_header(step + 1))

    def _build_project_bar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=9)
        self.project_bar = bar
        bar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            bar, text="PROYECTO ACTIVO", font=(FONT, 10, "bold"), text_color=MUTED
        ).grid(row=0, column=0, padx=(14, 10), pady=10)
        self.project_path = ctk.CTkLabel(
            bar,
            text=self.manager.project_path,
            font=(FONT, 12),
            text_color=TEXT,
            anchor="w",
        )
        self.project_path.grid(row=0, column=1, sticky="ew")
        self.context_badge = ctk.CTkLabel(
            bar, text="", font=(FONT, 11), text_color=MUTED
        )
        self.context_badge.grid(row=0, column=2, padx=10)
        ui_button(bar, "Cambiar…", self.choose_project, width=90).grid(
            row=0, column=3, padx=(0, 10), pady=7
        )
        ui_button(bar, "↻", self.refresh_context, width=38).grid(
            row=0, column=4, padx=(0, 10), pady=7
        )

    def _build_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        body = self.workspace
        body.grid(row=2, column=0, padx=20, sticky="nsew")
        body.grid_columnconfigure(0, weight=2, uniform="body")
        body.grid_columnconfigure(1, weight=3, uniform="body")
        body.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=10)
        left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(left, fg_color="transparent")
        top.grid(row=0, column=0, padx=14, pady=(12, 7), sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top, text="Biblioteca", font=(TITLE_FONT, 19), text_color=TEXT
        ).grid(row=0, column=0, sticky="w")
        ui_button(top, "+ Nuevo", self.open_editor, primary=True, width=82).grid(
            row=0, column=1
        )
        ui_button(top, "Importar", self.import_prompt, width=72).grid(
            row=0, column=2, padx=(6, 0)
        )
        self.search_var = ctk.StringVar()
        self.search_entry = ui_entry(
            left,
            textvariable=self.search_var,
            placeholder_text="Buscar título, etiqueta o contenido…",
        )
        self.search_entry.grid(row=1, column=0, padx=14, pady=(0, 8), sticky="ew")
        self.search_var.trace_add("write", lambda *_: self.refresh_prompts())
        self.prompt_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.prompt_list.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="nsew")
        self.prompt_list.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(6, weight=1)
        self.prompt_title = ctk.CTkLabel(
            right,
            text="Selecciona un prompt",
            font=(TITLE_FONT, 21),
            text_color=TEXT,
            anchor="w",
        )
        self.prompt_title.grid(row=0, column=0, padx=16, pady=(14, 2), sticky="ew")
        self.prompt_description = ctk.CTkLabel(
            right,
            text="El resultado contextualizado aparecerá aquí.",
            font=(FONT, 12),
            text_color=MUTED,
            anchor="w",
            wraplength=600,
            justify="left",
        )
        self.prompt_description.grid(row=1, column=0, padx=16, sticky="ew")
        self.tags_label = ctk.CTkLabel(
            right, text="", font=(FONT, 11, "bold"), text_color=ORANGE, anchor="w"
        )
        self.tags_label.grid(row=2, column=0, padx=16, pady=(4, 8), sticky="ew")
        switch = ctk.CTkFrame(right, fg_color="transparent")
        switch.grid(row=3, column=0, padx=16, sticky="ew")
        self.preview_mode = ctk.StringVar(value="Contextualizado")
        ctk.CTkSegmentedButton(
            switch,
            values=["Contextualizado", "Plantilla"],
            variable=self.preview_mode,
            command=lambda _value: self.update_preview(),
            selected_color=ORANGE,
            selected_hover_color=ORANGE_HOVER,
            unselected_color=INPUT,
            unselected_hover_color=BORDER,
            text_color=TEXT,
        ).pack(side="left")
        ui_button(switch, "Historial", self.show_history, width=82).pack(side="right")
        ui_button(switch, "Editar", self.edit_selected, width=70).pack(
            side="right", padx=6
        )
        ui_button(switch, "Duplicar", self.duplicate_selected, width=76).pack(
            side="right"
        )
        self.preview_status = ctk.CTkLabel(
            right, text="", font=(FONT, 11), text_color=MUTED, anchor="w"
        )
        self.preview_status.grid(row=4, column=0, padx=16, pady=(7, 3), sticky="ew")
        self.variables_frame = ctk.CTkScrollableFrame(
            right, fg_color="transparent", height=126
        )
        self.variables_frame.grid(row=5, column=0, padx=16, sticky="ew")
        self.variables_frame.grid_columnconfigure(1, weight=1)
        self.preview = ctk.CTkTextbox(
            right,
            fg_color=INPUT,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
            font=("Consolas", 12),
            wrap="word",
        )
        self.preview.grid(row=6, column=0, padx=16, pady=(5, 10), sticky="nsew")
        self.preview.configure(state="disabled")
        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=7, column=0, padx=16, pady=(0, 14), sticky="ew")
        self.copy_context_btn = ui_button(
            actions,
            "Copiar contextualizado",
            self.copy_contextual,
            primary=True,
            width=175,
        )
        self.copy_context_btn.pack(side="right")
        ui_button(actions, "Copiar plantilla", self.copy_template, width=125).pack(
            side="right", padx=7
        )
        ui_button(actions, "Exportar…", self.export_selected, width=92).pack(
            side="left"
        )
        ui_button(actions, "Eliminar", self.delete_selected, width=82).pack(
            side="left", padx=7
        )
        self._build_settings_view()

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(
            footer, text="Listo", font=(FONT, 11), text_color=MUTED, anchor="w"
        )
        self.status.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            footer,
            text="Local · no envía datos · v0.2.0",
            font=(FONT, 11),
            text_color=MUTED,
        ).grid(row=0, column=1)

    def _build_settings_view(self):
        self.settings_view = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10)
        self.settings_view.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            self.settings_view,
            text="Preferencias",
            font=(TITLE_FONT, 22),
            text_color=TEXT,
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=24, pady=(22, 14), sticky="ew")
        ctk.CTkLabel(
            self.settings_view,
            text="Historial de la biblioteca",
            font=(FONT, 12, "bold"),
            text_color=TEXT,
        ).grid(row=1, column=0, padx=24, pady=10, sticky="w")
        self.versioning_setting = ctk.CTkCheckBox(
            self.settings_view,
            text="Crear una versión Git al guardar o eliminar",
            fg_color=ORANGE,
            text_color=TEXT,
        )
        self.versioning_setting.grid(row=1, column=1, padx=24, pady=10, sticky="w")
        if self.store.settings.auto_version:
            self.versioning_setting.select()
        ctk.CTkLabel(
            self.settings_view,
            text=(
                "El historial pertenece a la biblioteca local y nunca modifica "
                "el proyecto activo."
            ),
            font=(FONT, 11),
            text_color=MUTED,
            wraplength=620,
            justify="left",
        ).grid(row=2, column=1, padx=24, sticky="w")
        ctk.CTkLabel(
            self.settings_view,
            text="Apariencia",
            font=(FONT, 12, "bold"),
            text_color=TEXT,
        ).grid(row=3, column=0, padx=24, pady=14, sticky="w")
        self.theme_setting = ctk.CTkOptionMenu(
            self.settings_view,
            values=["Dark", "Light"],
            fg_color=INPUT,
            button_color=BORDER,
            text_color=TEXT,
            height=34,
        )
        self.theme_setting.set(self.store.settings.theme)
        self.theme_setting.grid(row=3, column=1, padx=24, pady=14, sticky="w")
        ctk.CTkLabel(
            self.settings_view, text="Escala", font=(FONT, 12, "bold"), text_color=TEXT
        ).grid(row=4, column=0, padx=24, pady=10, sticky="w")
        self.scale_setting = ctk.CTkOptionMenu(
            self.settings_view,
            values=["90%", "100%", "110%", "125%"],
            fg_color=INPUT,
            button_color=BORDER,
            text_color=TEXT,
            height=34,
        )
        self.scale_setting.set(f"{self.store.settings.ui_scale}%")
        self.scale_setting.grid(row=4, column=1, padx=24, pady=10, sticky="w")
        actions = ctk.CTkFrame(self.settings_view, fg_color="transparent")
        actions.grid(row=5, column=0, columnspan=2, padx=24, pady=24, sticky="e")
        ui_button(actions, "Cancelar", self.close_settings, width=90).pack(
            side="left", padx=7
        )
        ui_button(
            actions, "Guardar preferencias", self.save_settings, primary=True, width=150
        ).pack(side="left")
        self.settings_view.grid_remove()

    def save_settings(self):
        self.store.settings.auto_version = bool(self.versioning_setting.get())
        self.store.settings.theme = self.theme_setting.get()
        self.store.settings.ui_scale = int(self.scale_setting.get().rstrip("%"))
        self.store.save()
        self._apply_settings()
        self.close_settings()

    def close_settings(self):
        self.settings_view.grid_remove()
        self.workspace.grid(row=2, column=0, padx=20, sticky="nsew")
        self.project_bar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.settings_btn.configure(text="⚙  Preferencias", command=self.open_settings)

    def choose_project(self):
        folder = filedialog.askdirectory(
            parent=self,
            title="Selecciona el proyecto a analizar",
            initialdir=self.manager.project_path,
        )
        if folder:
            try:
                self.manager.set_active_project(folder)
                self.store.settings.active_project = folder
                self.store.save()
                self.project_path.configure(text=folder)
                self.refresh_context()
            except ValueError as exc:
                messagebox.showerror("Proyecto activo", str(exc), parent=self)

    def refresh_context(self):
        if self.context_future and not self.context_future.done():
            return
        self.context_badge.configure(text="Analizando…")
        self.status.configure(text="Analizando el proyecto activo…", text_color=MUTED)
        self.context_future = self.executor.submit(self.manager.context, True)
        self.after(80, self._poll_context)

    def _poll_context(self):
        if not self.context_future:
            return
        if not self.context_future.done():
            self.after(80, self._poll_context)
            return
        try:
            context = self.context_future.result()
            stack = ", ".join(context.get("tech_stack", [])) or "Stack no detectado"
            self.context_badge.configure(
                text=f"{stack} · {'tests' if context.get('has_tests') else 'sin tests'}"
            )
            self.status.configure(
                text=f"Contexto actualizado: {context.get('project_name')}",
                text_color=SUCCESS,
            )
            if self.selected_filename:
                self._build_variable_fields()
                self.update_preview()
            else:
                self.refresh_prompts()
        except (OSError, ValueError) as exc:
            self.status.configure(text=str(exc), text_color=ERROR)
        finally:
            self.context_future = None

    def refresh_prompts(self):
        for widget in self.prompt_list.winfo_children():
            widget.destroy()
        query = self.search_var.get().strip()
        try:
            prompts = self.manager.search_prompts(query)
        except Exception as exc:
            prompts = []
            self.status.configure(text=f"Búsqueda no válida: {exc}", text_color=ERROR)
        self.prompt_buttons = {}
        for row, prompt in enumerate(prompts):
            filename = prompt.get("filename") or prompt.get("path")
            card = ctk.CTkButton(
                self.prompt_list,
                text=f"{prompt.get('name', filename)}\n{prompt.get('description', '')}",
                command=lambda value=filename: self.select_prompt(value),
                anchor="w",
                height=56,
                corner_radius=8,
                border_width=1,
                border_color=BORDER,
                fg_color="transparent",
                hover_color=INPUT,
                text_color=TEXT,
                font=(FONT, 12),
            )
            card.grid(row=row, column=0, padx=4, pady=3, sticky="ew")
            self.prompt_buttons[filename] = card
        if prompts and not self.selected_filename:
            first = prompts[0].get("filename") or prompts[0].get("path")
            self.select_prompt(first)
        if not prompts:
            ctk.CTkLabel(
                self.prompt_list,
                text="No se encontraron prompts.",
                text_color=MUTED,
                font=(FONT, 12),
            ).grid(row=0, column=0, pady=30)

    def select_prompt(self, filename):
        try:
            prompt = self.manager.get_prompt(filename)
        except (OSError, ValueError) as exc:
            self.status.configure(text=f"No se pudo abrir: {exc}", text_color=ERROR)
            return
        self.selected_filename = filename
        for key, control in self.prompt_buttons.items():
            control.configure(
                fg_color=INPUT if key == filename else "transparent",
                border_color=ORANGE if key == filename else BORDER,
            )
        self.prompt_title.configure(text=prompt["name"])
        self.prompt_description.configure(text=prompt["description"])
        self.tags_label.configure(text="  ·  ".join(prompt.get("tags", [])))
        self._build_variable_fields()
        self.update_preview()

    def _build_variable_fields(self):
        for widget in self.variables_frame.winfo_children():
            widget.destroy()
        self.variable_entries = {}
        if not self.selected_filename:
            return
        variables = self.manager.required_variables(self.selected_filename)
        for row, name in enumerate(variables):
            friendly = name.replace("_", " ").capitalize()
            ctk.CTkLabel(
                self.variables_frame,
                text=friendly,
                font=(FONT, 11),
                text_color=MUTED,
                anchor="w",
            ).grid(row=row, column=0, padx=(0, 8), pady=3, sticky="w")
            initial = self.session_drafts.get(self.selected_filename, {}).get(name, "")
            multiline = any(
                token in name.lower()
                for token in (
                    "codigo",
                    "code",
                    "logs",
                    "sql",
                    "json",
                    "requisitos",
                    "contenido",
                )
            )
            if multiline:
                control = ctk.CTkTextbox(
                    self.variables_frame,
                    height=72,
                    fg_color=INPUT,
                    text_color=TEXT,
                    border_width=1,
                    border_color=BORDER,
                    font=("Consolas", 11),
                )
                control.insert("1.0", initial)
                control.bind("<KeyRelease>", lambda _event: self._variable_changed())
                control.grid(row=row, column=1, pady=3, sticky="ew")
                self.variable_entries[name] = (control, "textbox")
            else:
                value = ctk.StringVar(value=initial)
                value.trace_add("write", lambda *_: self._variable_changed())
                control = ui_entry(
                    self.variables_frame,
                    textvariable=value,
                    placeholder_text=f"Escribe {friendly.lower()}",
                )
                control.grid(row=row, column=1, pady=3, sticky="ew")
                self.variable_entries[name] = (value, "variable")

    def _variable_changed(self):
        if self.selected_filename:
            self.session_drafts[self.selected_filename] = self._variable_values()
        self.update_preview()

    def _variable_values(self):
        values = {}
        for name, (control, kind) in self.variable_entries.items():
            values[name] = (
                control.get("1.0", "end-1c") if kind == "textbox" else control.get()
            )
        return values

    def update_preview(self):
        if not self.selected_filename:
            return
        try:
            if self.preview_mode.get() == "Contextualizado":
                text = self.manager.render_prompt(
                    self.selected_filename, self._variable_values()
                )
                status = "Vista final con el contexto del proyecto activo"
            else:
                text = self.manager.get_prompt(self.selected_filename)["template"]
                status = "Plantilla Jinja2 original"
            self._set_preview(text)
            self.preview_status.configure(text=status, text_color=MUTED)
            self.copy_context_btn.configure(state="normal")
        except (OSError, ValueError) as exc:
            self._set_preview(str(exc))
            self.preview_status.configure(
                text="Falta contexto o la plantilla es inválida", text_color=ERROR
            )
            self.copy_context_btn.configure(state="disabled")

    def _set_preview(self, text):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def copy_contextual(self):
        if not self.selected_filename:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(
                self.manager.render_prompt(
                    self.selected_filename, self._variable_values()
                )
            )
            self.status.configure(
                text="Prompt contextualizado copiado", text_color=SUCCESS
            )
        except ValueError as exc:
            self.status.configure(text=str(exc), text_color=ERROR)

    def copy_template(self):
        if self.selected_filename:
            self.clipboard_clear()
            self.clipboard_append(
                self.manager.get_prompt(self.selected_filename)["template"]
            )
            self.status.configure(text="Plantilla copiada", text_color=SUCCESS)

    def export_selected(self):
        if not self.selected_filename:
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("JSON", "*.json"), ("YAML", "*.yaml")],
        )
        if path:
            fmt = {".md": "markdown", ".json": "json"}.get(
                Path(path).suffix.lower(), "yaml"
            )
            Path(path).write_text(
                self.manager.export_prompt(
                    self.selected_filename, fmt, self._variable_values()
                ),
                encoding="utf-8",
            )
            self.status.configure(text=f"Exportado: {path}", text_color=SUCCESS)

    def delete_selected(self):
        if not self.selected_filename:
            return
        prompt = self.manager.get_prompt(self.selected_filename)
        if not messagebox.askyesno(
            "Eliminar prompt",
            f"¿Eliminar '{prompt['name']}' de la biblioteca?",
            parent=self,
        ):
            return
        try:
            self.manager.delete_prompt(self.selected_filename)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Eliminar prompt", str(exc), parent=self)
            return
        self.selected_filename = None
        self.prompt_title.configure(text="Selecciona un prompt")
        self.prompt_description.configure(text="El prompt fue eliminado.")
        self.tags_label.configure(text="")
        self._set_preview("")
        self.refresh_prompts()
        self.status.configure(text="Prompt eliminado", text_color=SUCCESS)

    def open_editor(self, prompt=None):
        EditorDialog(self, self.manager, prompt, self._after_save)

    def import_prompt(self):
        source = filedialog.askopenfilename(
            parent=self,
            title="Importar prompt YAML",
            filetypes=[("YAML", "*.yaml *.yml")],
        )
        if not source:
            return
        try:
            import yaml

            data = yaml.safe_load(Path(source).read_text(encoding="utf-8"))
            filename = self.manager._safe_filename(Path(source).name)
            if (self.manager.prompts_dir / filename).exists():
                raise ValueError("Ya existe un prompt con ese nombre de archivo.")
            self.manager.add_prompt(filename, data)
        except Exception as exc:
            messagebox.showerror("Importar prompt", str(exc), parent=self)
            return
        self._after_save(filename)

    def duplicate_selected(self):
        if not self.selected_filename:
            return
        prompt = self.manager.get_prompt(self.selected_filename)
        stem = Path(self.selected_filename).stem
        counter = 2
        while (self.manager.prompts_dir / f"{stem}_{counter}.yaml").exists():
            counter += 1
        filename = f"{stem}_{counter}.yaml"
        prompt["name"] += " (copia)"
        self.manager.add_prompt(filename, prompt)
        self._after_save(filename)

    def edit_selected(self):
        if self.selected_filename:
            self.open_editor(
                {
                    **self.manager.get_prompt(self.selected_filename),
                    "filename": self.selected_filename,
                }
            )

    def _after_save(self, filename):
        self.selected_filename = filename
        self.refresh_prompts()
        self.select_prompt(filename)
        self.status.configure(text="Prompt guardado", text_color=SUCCESS)

    def show_history(self):
        if not self.selected_filename:
            return
        records = self.manager.get_history(self.selected_filename)
        text = "\n\n".join(
            f"{item['date']}  {item['message']}\n{item['hash'][:10]} · {item['author']}"
            for item in records
        )
        TextDialog(
            self, "Historial Git", text or "Este prompt todavía no tiene historial Git."
        )

    def open_settings(self):
        self.workspace.grid_remove()
        self.project_bar.grid_remove()
        self.settings_view.grid(row=1, column=0, rowspan=2, padx=20, sticky="nsew")
        self.settings_btn.configure(text="←  Volver", command=self.close_settings)

    def _apply_settings(self):
        self.manager.auto_version = self.store.settings.auto_version
        ctk.set_appearance_mode(self.store.settings.theme)
        ctk.set_widget_scaling(self.store.settings.ui_scale / 100)
        self.status.configure(text="Preferencias guardadas", text_color=SUCCESS)

    def _close_app(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()


class EditorDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager, prompt, callback):
        super().__init__(parent)
        self.manager, self.prompt, self.callback = manager, prompt, callback
        self.title("Editar prompt" if prompt else "Nuevo prompt")
        self.geometry("720x650")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self._label("Nombre", 0)
        self.name = ui_entry(self)
        self.name.grid(row=1, column=0, padx=20, sticky="ew")
        self._label("Archivo", 2)
        self.filename = ui_entry(self, placeholder_text="mi_prompt.yaml")
        self.filename.grid(row=3, column=0, padx=20, sticky="ew")
        self._label("Descripción", 4)
        self.description = ui_entry(self)
        self.description.grid(row=5, column=0, padx=20, sticky="ew")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="ew")
        ctk.CTkLabel(
            row, text="Plantilla Jinja2", text_color=TEXT, font=(FONT, 12, "bold")
        ).pack(side="left")
        ctk.CTkLabel(
            row,
            text="Variables: {{ project_name }}, {{ tech_stack }}, {{ languages }}",
            text_color=MUTED,
            font=(FONT, 11),
        ).pack(side="right")
        self.template = ctk.CTkTextbox(
            self,
            fg_color=INPUT,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            font=("Consolas", 12),
        )
        self.template.grid(row=7, column=0, padx=20, sticky="nsew")
        self._label("Etiquetas separadas por comas", 8)
        self.tags = ui_entry(self)
        self.tags.grid(row=9, column=0, padx=20, sticky="ew")
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=10, column=0, padx=20, pady=18, sticky="e")
        ui_button(actions, "Cancelar", self.destroy, width=90).pack(side="left", padx=6)
        ui_button(actions, "Guardar prompt", self.save, primary=True, width=130).pack(
            side="left"
        )
        if prompt:
            self.name.insert(0, prompt["name"])
            self.filename.insert(0, prompt["filename"])
            self.filename.configure(state="disabled")
            self.description.insert(0, prompt["description"])
            self.template.insert("1.0", prompt["template"])
            self.tags.insert(0, ", ".join(prompt.get("tags", [])))

    def _label(self, text, row):
        ctk.CTkLabel(
            self, text=text, text_color=TEXT, font=(FONT, 12, "bold"), anchor="w"
        ).grid(row=row, column=0, padx=20, pady=(10, 4), sticky="ew")

    def save(self):
        filename = (
            self.prompt["filename"] if self.prompt else self.filename.get().strip()
        )
        data = {
            "name": self.name.get().strip(),
            "description": self.description.get().strip(),
            "template": self.template.get("1.0", "end-1c"),
            "tags": [
                item.strip() for item in self.tags.get().split(",") if item.strip()
            ],
            "version": self.prompt.get("version", "0.1.0") if self.prompt else "0.1.0",
        }
        try:
            self.manager.add_prompt(filename, data)
        except Exception as exc:
            messagebox.showerror("Guardar prompt", str(exc), parent=self)
            return
        self.callback(self.manager._safe_filename(filename))
        self.destroy()


class TextDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        self.geometry("660x480")
        self.transient(parent)
        box = ctk.CTkTextbox(
            self, font=("Consolas", 12), fg_color=INPUT, text_color=TEXT
        )
        box.pack(fill="both", expand=True, padx=16, pady=16)
        box.insert("1.0", content)
        box.configure(state="disabled")


def main():
    RSPromptManagerGUI().mainloop()


if __name__ == "__main__":
    main()
