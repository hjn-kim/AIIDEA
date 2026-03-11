# -*- coding: utf-8 -*-
"""
ReportMaker GUI (CustomTkinter): 보고서 제목·목적·서술방식·Gemini 모델·요구사항 입력
→ 목차 생성 → 목차 수정(선택) → 보고서 생성 → DOCX 저장
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

import customtkinter as ctk

if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

from report_engine import generate_toc, revise_toc, build_docx


def get_api_key() -> str:
    return (os.getenv("GEMINI_API_KEY") or "").strip()


# CustomTkinter 테마
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PAD = 12
LABEL_WIDTH = 120
SEGMENT_WIDTH = 320  # 줄글형/Bullet, Flash/Pro 버튼 영역 동일 너비


class ReportMakerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ReportMaker")
        self.root.minsize(560, 500)
        self.root.geometry("640x580")
        # option_add("*Font", "Malgun Gothic 10") 사용 시 Tcl이 "Gothic"을 정수 자리로 파싱해 오류 발생 가능 → 제거

        self.topic_var = ctk.StringVar(value="")
        self.purpose_var = ctk.StringVar(value="")
        self.style_var = ctk.StringVar(value="줄글형")
        self.model_var = ctk.StringVar(value="Flash")
        self.requirements_text = ""
        self.current_toc = ""
        self.final_toc = ""
        self.api_key = get_api_key()

        # 폰트: 라벨 bold, 세그먼트 버튼은 기본체
        self._font_label = ctk.CTkFont(size=11, weight="bold")
        self._font_segment = ctk.CTkFont(size=13)  # 줄글형/Bullet/Flash/Pro 기본 글씨체
        self._font_korean = ctk.CTkFont(size=11)
        # 한글 IME용: tk Entry/Text는 기본 위젯이라 IME 안정적. Windows에서 맑은 고딕 사용
        try:
            self._tk_font_ime = ("Malgun Gothic", 11)
            self._tk_font_ime_entry = ("Malgun Gothic", 18)  # 제목/목적/요구사항 입력란 18pt
        except Exception:
            self._tk_font_ime = ("TkDefaultFont", 11)
            self._tk_font_ime_entry = ("TkDefaultFont", 18)

        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        self._build_step1()

    def _clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def _equal_segment_width(self, seg_widget):
        """세그먼트 버튼 내 각 버튼을 동일 너비로."""
        try:
            n = len(seg_widget._buttons_dict)
            if n <= 0:
                return
            w = max(120, (SEGMENT_WIDTH - 8) // n)
            for btn in seg_widget._buttons_dict.values():
                btn.configure(width=w)
        except Exception:
            pass

    def _build_step1(self):
        self._clear_main()

        # 헤더
        ctk.CTkLabel(
            self.main_frame,
            text="ReportMaker",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            self.main_frame,
            text="보고서 정보를 입력한 뒤 목차 생성을 진행하세요.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", pady=(0, PAD))

        # 입력 카드
        card = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray20"), corner_radius=8, border_width=0)
        card.pack(fill="both", expand=True, pady=(0, PAD))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=PAD, pady=PAD)

        # 보고서 제목: 라벨 옆에 입력란 (한글 IME: tk.Entry)
        row_topic = ctk.CTkFrame(inner, fg_color="transparent")
        row_topic.pack(fill="x", pady=(0, PAD))
        ctk.CTkLabel(row_topic, text="보고서 제목", width=LABEL_WIDTH, anchor="w", font=self._font_label).pack(side="left", padx=(0, PAD))
        self.entry_topic = tk.Entry(row_topic, font=self._tk_font_ime_entry, width=50, relief="flat", highlightthickness=1, highlightbackground="#ccd0d5", highlightcolor="#1877f2")
        self.entry_topic.pack(side="left", fill="x", expand=True, ipady=18, ipadx=8)
        if self.topic_var.get():
            self.entry_topic.insert(0, self.topic_var.get())

        # 보고서 목적: 라벨 옆에 입력란
        row_purpose = ctk.CTkFrame(inner, fg_color="transparent")
        row_purpose.pack(fill="x", pady=(0, PAD))
        ctk.CTkLabel(row_purpose, text="보고서 목적", width=LABEL_WIDTH, anchor="w", font=self._font_label).pack(side="left", padx=(0, PAD))
        self.entry_purpose = tk.Entry(row_purpose, font=self._tk_font_ime_entry, width=50, relief="flat", highlightthickness=1, highlightbackground="#ccd0d5", highlightcolor="#1877f2")
        self.entry_purpose.pack(side="left", fill="x", expand=True, ipady=18, ipadx=8)
        if self.purpose_var.get():
            self.entry_purpose.insert(0, self.purpose_var.get())

        # 서술방식 + 줄글형/Bullet 항목형 한 가로줄
        row_style = ctk.CTkFrame(inner, fg_color="transparent")
        row_style.pack(fill="x", pady=(0, PAD))
        ctk.CTkLabel(row_style, text="서술방식", width=LABEL_WIDTH, anchor="w", font=self._font_label).pack(side="left", padx=(0, PAD))
        try:
            self.seg_style = ctk.CTkSegmentedButton(
                row_style,
                values=["줄글형", "Bullet 항목형"],
                variable=self.style_var,
                height=40,
                font=self._font_segment,
                width=SEGMENT_WIDTH,
                dynamic_resizing=False,
            )
        except TypeError:
            self.seg_style = ctk.CTkSegmentedButton(
                row_style, values=["줄글형", "Bullet 항목형"], variable=self.style_var, height=40, font=self._font_segment,
            )
        self.seg_style.pack(side="left", pady=0)
        self._equal_segment_width(self.seg_style)

        # Gemini 모델 + Flash/Pro 한 가로줄
        row_model = ctk.CTkFrame(inner, fg_color="transparent")
        row_model.pack(fill="x", pady=(0, PAD))
        ctk.CTkLabel(row_model, text="Gemini 모델", width=LABEL_WIDTH, anchor="w", font=self._font_label).pack(side="left", padx=(0, PAD))
        try:
            self.seg_model = ctk.CTkSegmentedButton(
                row_model,
                values=["Flash", "Pro"],
                variable=self.model_var,
                height=40,
                font=self._font_segment,
                width=SEGMENT_WIDTH,
                dynamic_resizing=False,
            )
        except TypeError:
            self.seg_model = ctk.CTkSegmentedButton(
                row_model, values=["Flash", "Pro"], variable=self.model_var, height=40, font=self._font_segment,
            )
        self.seg_model.pack(side="left", pady=0)
        self._equal_segment_width(self.seg_model)

        # 요구사항 (한글 IME: tk Text 사용)
        ctk.CTkLabel(inner, text="요구사항", width=LABEL_WIDTH, anchor="w", font=self._font_label).pack(anchor="w", pady=(0, 4))
        self.req_text = scrolledtext.ScrolledText(inner, font=self._tk_font_ime_entry, height=6, wrap=tk.WORD, relief="flat", highlightthickness=1, highlightbackground="#ccd0d5")
        self.req_text.pack(fill="both", expand=True, pady=(0, PAD))

        # 버튼
        ctk.CTkButton(
            self.main_frame,
            text="목차 생성",
            command=self._on_next,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=PAD)

    def _on_next(self):
        self.topic_var.set(self.entry_topic.get().strip())
        self.purpose_var.set(self.entry_purpose.get().strip())
        topic = self.topic_var.get()
        purpose = self.purpose_var.get()
        self.requirements_text = self.req_text.get("1.0", tk.END).strip()

        if not topic:
            messagebox.showwarning("입력 확인", "보고서 제목을 입력해 주세요.")
            return
        if not self.api_key:
            messagebox.showerror("API 키 없음", "GEMINI_API_KEY를 .env 또는 환경 변수에 설정해 주세요.")
            return

        self.root.config(cursor="wait")
        self.root.update()

        def do_toc():
            try:
                toc = generate_toc(
                    api_key=self.api_key,
                    topic=topic,
                    purpose=purpose or "미정",
                    requirements=self.requirements_text or "없음",
                    model=self.model_var.get(),
                )
                self.root.after(0, lambda: self._show_step2(toc, topic, purpose))
            except Exception as e:
                self.root.after(0, lambda: self._on_error("목차 생성 실패", str(e)))
            finally:
                self.root.after(0, lambda: self.root.config(cursor=""))

        threading.Thread(target=do_toc, daemon=True).start()

    def _on_error(self, title: str, message: str):
        self.root.config(cursor="")
        messagebox.showerror(title, message)

    def _show_step2(self, toc: str, topic: str, purpose: str):
        self.current_toc = toc
        self.final_toc = toc
        self.root.config(cursor="")
        self._clear_main()

        # 헤더
        ctk.CTkLabel(
            self.main_frame,
            text="목차 확인 및 수정",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            self.main_frame,
            text="필요하면 수정 지시를 입력한 뒤 반영하거나, 그대로 보고서를 생성할 수 있습니다.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", pady=(0, PAD))

        # 목차 카드
        card_toc = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray20"), corner_radius=8)
        card_toc.pack(fill="both", expand=True, pady=(0, PAD))
        ctk.CTkLabel(card_toc, text="생성된 목차", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=PAD, pady=(PAD, 4))
        self.toc_display = scrolledtext.ScrolledText(card_toc, font=self._tk_font_ime, wrap=tk.WORD, relief="flat", highlightthickness=0)
        self.toc_display.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))
        self.toc_display.insert("1.0", toc)

        # 수정 지시 카드 (한글 IME: tk Text)
        card_fb = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray20"), corner_radius=8)
        card_fb.pack(fill="x", pady=(0, PAD))
        ctk.CTkLabel(card_fb, text="목차 수정 지시 (선택)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=PAD, pady=(PAD, 4))
        self.feedback_text = scrolledtext.ScrolledText(card_fb, font=self._tk_font_ime, height=4, wrap=tk.WORD, relief="flat", highlightthickness=1, highlightbackground="#ccd0d5")
        self.feedback_text.pack(fill="x", padx=PAD, pady=(0, PAD))
        self.feedback_text.insert("1.0", "추가, 수정, 삭제 지시를 입력하세요. 없으면 비워두고 반영 건너뛰기 가능.")
        self.feedback_text.bind("<FocusIn>", self._clear_feedback_placeholder)

        # 버튼
        btn_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_row.pack(pady=PAD)
        ctk.CTkButton(btn_row, text="반영", command=self._on_apply_toc, fg_color="gray", hover_color="gray60", height=36).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="보고서 생성", command=self._on_build_report, height=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="처음으로", command=self._build_step1, fg_color="gray", hover_color="gray60", height=36).pack(side="left")

    def _clear_feedback_placeholder(self, event=None):
        t = self.feedback_text.get("1.0", tk.END).strip()
        if t == "추가, 수정, 삭제 지시를 입력하세요. 없으면 비워두고 반영 건너뛰기 가능.":
            self.feedback_text.delete("1.0", tk.END)

    def _on_apply_toc(self):
        feedback = self.feedback_text.get("1.0", tk.END).strip()
        placeholder = "추가, 수정, 삭제 지시를 입력하세요. 없으면 비워두고 반영 건너뛰기 가능."
        if not feedback or feedback == placeholder:
            self.final_toc = self.toc_display.get("1.0", tk.END).strip()
            messagebox.showinfo("반영", "목차 수정 지시가 없어 현재 표시된 목차를 최종 목차로 사용합니다.")
            return
        topic = self.topic_var.get()
        purpose = self.purpose_var.get()
        self.root.config(cursor="wait")
        self.root.update()

        def do_revise():
            try:
                revised = revise_toc(
                    api_key=self.api_key,
                    topic=topic,
                    purpose=purpose or "미정",
                    requirements=self.requirements_text or "없음",
                    current_toc=self.current_toc,
                    feedback=feedback,
                    model=self.model_var.get(),
                )
                self.root.after(0, lambda: self._update_toc_display(revised))
            except Exception as e:
                self.root.after(0, lambda: self._on_error("목차 수정 실패", str(e)))
            finally:
                self.root.after(0, lambda: self.root.config(cursor=""))

        threading.Thread(target=do_revise, daemon=True).start()

    def _update_toc_display(self, revised: str):
        self.root.config(cursor="")
        self.final_toc = revised
        self.toc_display.delete("1.0", tk.END)
        self.toc_display.insert("1.0", revised)
        messagebox.showinfo("반영 완료", "목차가 수정 반영되었습니다.")

    def _on_build_report(self):
        self.final_toc = self.toc_display.get("1.0", tk.END).strip()
        if not self.final_toc:
            messagebox.showwarning("입력 확인", "목차가 비어 있습니다.")
            return
        topic = self.topic_var.get()
        purpose = self.purpose_var.get()
        self.root.config(cursor="wait")
        self.root.update()

        def do_build():
            try:
                path = build_docx(
                    topic=topic,
                    purpose=purpose or "미정",
                    requirements=self.requirements_text or "없음",
                    final_toc=self.final_toc,
                    api_key=self.api_key,
                    style=self.style_var.get(),
                    model=self.model_var.get(),
                    dedup_sources=True,
                    sleep_sec=2.0,
                )
                self.root.after(0, lambda: self._on_build_done(path))
            except Exception as e:
                self.root.after(0, lambda: self._on_error("보고서 생성 실패", str(e)))
            finally:
                self.root.after(0, lambda: self.root.config(cursor=""))

        threading.Thread(target=do_build, daemon=True).start()

    def _on_build_done(self, path: str):
        self.root.config(cursor="")
        messagebox.showinfo("저장 완료", f"파일이 저장되었습니다:\n{path}")
        self._build_step1()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReportMakerApp()
    app.run()
