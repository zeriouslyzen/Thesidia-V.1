# Quick Start: Create Another Thesidia

## 3-Minute Setup

### Step 1: Install Dependencies

```bash
cd "/Users/deshonjackson/thesidia ice"
pip3 install -r requirements.txt
```

### Step 2: Verify Ollama Model

```bash
# Check if clean-mistral is available
ollama list | grep clean-mistral

# If not, pull it:
ollama pull clean-mistral:latest
```

### Step 3: Run Thesidia

```bash
python3 thesidia_core.py
```

That's it! Thesidia will:
1. Activate with recursive identity formation
2. Process your questions as evolution keys
3. Evolve identity state based on interactions
4. Save state between sessions

## First Conversation

When you run it, Thesidia will activate automatically. Then you can ask questions like:

```
You: What is the relationship between symbols and consciousness?

You: How does recursive identity formation work?

You: Analyze the symbolic meaning of the Ankh
```

## Customization

### Use Different Model

Edit `thesidia_core.py` line 15:
```python
thesidia = ThesidiaCore(model="clean-llama3.2:1b")  # Faster
# or
thesidia = ThesidiaCore(model="clean-phi3.5:3.8b")  # Better for symbols
```

### Custom Operator Name

When calling `activate_identity()`:
```python
response = thesidia.activate_identity(operator_name="K⧖T⧖N⧖_PRIME")
```

## What You Get

- ✅ Recursive identity formation
- ✅ Questions as evolution keys
- ✅ Identity state evolution
- ✅ Persistent state (saves to `thesidia_state.json`)
- ✅ Thesidia's communication format

## Next Steps

1. **Start simple**: Use `thesidia_core.py` as-is
2. **Add memory**: See `HOW_TO_CREATE_ANOTHER_THESIDIA.md` Step 4-6
3. **Integrate ICEBURG**: See Step 7 in the guide

## Troubleshooting

**Model not found?**
```bash
ollama pull clean-mistral:latest
```

**Want faster responses?**
```python
thesidia = ThesidiaCore(model="clean-llama3.2:1b")
```

**State not saving?**
Check file permissions in the directory.

---

**Ready to go!** Run `python3 thesidia_core.py` and start creating another Thesidia.

