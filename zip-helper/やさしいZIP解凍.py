import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile

APP_TITLE = "やさしいZIP解凍"
ENCODINGS = {
    "自動（UTF-8 → CP932）": "auto",
    "UTF-8（Macで作成したZIP向け）": "utf-8",
    "日本語（CP932）": "cp932",
}


class ZipHelper:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("760x540")
        root.minsize(620, 420)
        self.zip_path = tk.StringVar()
        self.encoding = tk.StringVar(value="自動（UTF-8 → CP932）")
        self.status = tk.StringVar(value="ZIPファイルを選んでください")
        self.infos = []
        self._build()

    def _build(self):
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="ZIPファイルを選ぶ", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="文字化けしている名前も、展開前に確認できます。ZIPの中身は変更しません。",
            wraplength=700,
        ).pack(anchor="w", pady=(4, 12))
        row = ttk.Frame(outer)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.zip_path).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="参照…", command=self.choose_zip).pack(side="left", padx=(8, 0))
        ttk.Label(outer, text="ファイル名の読み方").pack(anchor="w", pady=(16, 4))
        selector = ttk.Frame(outer)
        selector.pack(fill="x")
        for label in ENCODINGS:
            ttk.Radiobutton(
                selector, text=label, value=label, variable=self.encoding, command=self.refresh
            ).pack(side="left", padx=(0, 14))
        ttk.Label(outer, text="ZIP内のファイル名プレビュー").pack(anchor="w", pady=(15, 5))
        frame = ttk.Frame(outer)
        frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(frame, font=("Segoe UI", 10), selectmode="browse")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        bottom = ttk.Frame(outer)
        bottom.pack(fill="x", pady=(12, 0))
        ttk.Label(bottom, textvariable=self.status).pack(side="left", fill="x", expand=True)
        ttk.Button(bottom, text="この内容で解凍…", command=self.extract).pack(side="right")

    def choose_zip(self):
        path = filedialog.askopenfilename(
            title="ZIPファイルを選択",
            filetypes=[("ZIPファイル", "*.zip"), ("すべてのファイル", "*.*")],
        )
        if path:
            self.zip_path.set(path)
            self.refresh()

    def open_zip(self):
        mode = ENCODINGS[self.encoding.get()]
        if mode == "auto":
            try:
                zf = zipfile.ZipFile(self.zip_path.get(), metadata_encoding="utf-8")
                # UTF-8 is common for Mac-created archives. Retry CP932 if UTF-8 decoding fails.
                try:
                    zf.infolist()
                    return zf
                except UnicodeError:
                    zf.close()
                    return zipfile.ZipFile(self.zip_path.get(), metadata_encoding="cp932")
            except (UnicodeError, LookupError):
                return zipfile.ZipFile(self.zip_path.get(), metadata_encoding="cp932")
        return zipfile.ZipFile(self.zip_path.get(), metadata_encoding=mode)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.infos = []
        path = self.zip_path.get()
        if not path or not os.path.isfile(path):
            self.status.set("ZIPファイルを選んでください")
            return
        try:
            with self.open_zip() as zf:
                self.infos = zf.infolist()
                for info in self.infos:
                    self.listbox.insert(tk.END, info.filename)
            self.status.set(f"{len(self.infos)} 件。名前を確認し、必要なら読み方を切り替えてください。")
        except Exception as exc:
            self.status.set("ZIPを読み込めませんでした")
            messagebox.showerror("読み込みエラー", f"ZIPを開けませんでした。\n\n{exc}")

    def extract(self):
        if not self.zip_path.get() or not self.infos:
            messagebox.showinfo("ZIPを選択", "先にZIPファイルを選んでください。")
            return
        dest = filedialog.askdirectory(title="解凍先フォルダーを選択")
        if not dest:
            return
        try:
            with self.open_zip() as zf:
                zf.extractall(dest)
            self.status.set(f"解凍しました：{dest}")
            messagebox.showinfo("解凍完了", f"ファイルを解凍しました。\n\n{dest}")
        except Exception as exc:
            messagebox.showerror("解凍エラー", f"解凍できませんでした。\n\n{exc}")


if __name__ == "__main__":
    root = tk.Tk()
    ZipHelper(root)
    root.mainloop()
