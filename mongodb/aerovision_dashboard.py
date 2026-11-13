"""AeroVision Navigation Event Analysis - small Tkinter dashboard on top of MongoDB.
Run:  pip install pymongo   then   python aerovision_dashboard.py
Needs MongoDB running on localhost:27017 (events are in aerovision_db.events)."""
import csv, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pymongo import MongoClient

URI = "mongodb://localhost:27017"
coll = MongoClient(URI, serverSelectionTimeoutMS=3000)["aerovision_db"]["events"]
COLS = ("Date", "Zone", "Mode", "Event Type", "Severity", "Response (ms)")

root = tk.Tk()
root.title("AeroVision Navigation Event Analysis")
root.geometry("900x560")

top = ttk.Frame(root); top.pack(fill="x", padx=10, pady=6)
ttk.Label(top, text=f"MongoDB: {URI}").pack(side="left")
status = tk.StringVar()
ttk.Label(root, textvariable=status).pack(anchor="w", padx=10, pady=4)

tree = ttk.Treeview(root, show="headings")
tree.pack(fill="both", expand=True, padx=10, pady=6)

def setup(cols):
    tree["columns"] = cols
    for c in cols:
        tree.heading(c, text=c); tree.column(c, anchor="center", width=140)
    tree.delete(*tree.get_children())

def show_records():
    setup(COLS)
    total = coll.count_documents({})
    for d in coll.find({}, {"_id": 0}).limit(500):
        tree.insert("", "end", values=(d["date"], d["zone"], d["mode"], d["event_type"], d["severity"], d["response_ms"]))
    status.set(f"Showing up to 500 of {total:,} records")

def by_type():
    setup(("Group", "Event Type", "Count"))
    rows = list(coll.aggregate([{"$group": {"_id": "$event_type", "total": {"$sum": 1}}}, {"$sort": {"total": -1}}]))
    for r in rows: tree.insert("", "end", values=("Events by type", r["_id"], r["total"]))
    status.set(f"Events by type: {len(rows)} groups.")

def avg_mode():
    setup(("Group", "Mode", "Average response (ms)"))
    rows = list(coll.aggregate([{"$group": {"_id": "$mode", "avg_response_ms": {"$avg": "$response_ms"}}}, {"$sort": {"avg_response_ms": -1}}]))
    for r in rows: tree.insert("", "end", values=("Average response by mode", r["_id"], round(r["avg_response_ms"], 4)))
    status.set(f"Average response by mode: {len(rows)} groups. Average response is in milliseconds.")

def high_sev():
    setup(COLS)
    q = {"severity": {"$in": ["High", "Critical"]}}
    for d in coll.find(q, {"_id": 0}).limit(500):
        tree.insert("", "end", values=(d["date"], d["zone"], d["mode"], d["event_type"], d["severity"], d["response_ms"]))
    status.set(f"High and Critical events: {coll.count_documents(q):,}")

def import_csv():
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not path: return
    with open(path, newline="") as f:
        docs = [dict(r, response_ms=int(r["response_ms"])) for r in csv.DictReader(f)]
    coll.delete_many({}); coll.insert_many(docs)
    messagebox.showinfo("Import", f"Imported {len(docs):,} records")
    show_records()

for text, cmd in [("Events by type", by_type), ("Average response by mode", avg_mode), ("High severity count", high_sev)]:
    ttk.Button(root, text=text, command=cmd).pack(side="left", padx=10, pady=4)
ttk.Button(top, text="Import CSV", command=import_csv).pack(side="right", padx=4)
ttk.Button(top, text="Refresh records", command=show_records).pack(side="right", padx=4)

try: show_records()
except Exception as e: status.set(f"Cannot reach MongoDB: {e}")
root.mainloop()
