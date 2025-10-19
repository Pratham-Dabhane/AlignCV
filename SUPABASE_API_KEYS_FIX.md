# 🔑 **Supabase API Keys Update Required**

## ❌ **Current Issue:**

The test shows:
```
signature verification failed
```

This means the **API keys in `.env` are not correct**.

---

## 🔧 **How to Fix:**

### **Step 1: Get Fresh API Keys from Supabase**

1. Go to: **https://app.supabase.com/project/cgmtifbpdujkcgkerkai/settings/api**

2. You'll see two keys:

   **A. Project API keys:**
   ```
   anon public: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnbXRpZmJwZHVqa2Nna2Vya2FpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk5NDA0NjIsImV4cCI6MjA0NTUxNjQ2Mn0.XXX...
   
   service_role secret: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnbXRpZmJwZHVqa2Nna2Vya2FpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyOTk0MDQ2MiwiZXhwIjoyMDQ1NTE2NDYyfQ.YYY...
   ```

3. **Copy both keys** (the full JWT tokens, starting with `eyJ...`)

---

### **Step 2: Update `.env` File**

Open [`.env`](.env ) and replace:

```env
# Current (wrong keys):
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...OLD_KEY
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...OLD_KEY

# Replace with fresh keys from dashboard:
SUPABASE_ANON_KEY=<PASTE_NEW_ANON_KEY_HERE>
SUPABASE_SERVICE_ROLE_KEY=<PASTE_NEW_SERVICE_ROLE_KEY_HERE>
```

**Important:** 
- Keys should start with `eyJ`
- Keys are very long (~200+ characters)
- Copy the FULL key (don't truncate)

---

### **Step 3: Create Storage Bucket (if not exists)**

1. Go to: **https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets**

2. If you DON'T see `aligncv-resumes` bucket:
   - Click **"New bucket"**
   - Name: `aligncv-resumes`
   - Privacy: **Private** (not public!)
   - Click **"Create bucket"**

3. If bucket already exists:
   - ✅ You're good!

---

### **Step 4: Test Again**

After updating keys:
```powershell
python test_supabase_storage.py
```

**Expected output:**
```
✅ File uploaded successfully!
✅ Storage path: user_999/20231019_123456_test_resume.txt
✅ File downloaded successfully!
```

---

## 📊 **Then When You Use Frontend:**

### **What Happens:**
1. User uploads resume through Streamlit frontend
2. File gets sent to backend API
3. Backend saves to Supabase Storage (bucket: `aligncv-resumes`)
4. File stored as: `user_123/20231019_143052_john_resume.pdf`

### **How to Verify in Dashboard:**
1. Go to: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets/aligncv-resumes
2. You'll see folders: `user_1/`, `user_2/`, etc.
3. Click on any folder → See uploaded resumes
4. Can download, view, or delete from dashboard

---

## 🔐 **Security Note:**

The **service_role** key has FULL access to your Supabase project:
- ⚠️ Keep it SECRET (never commit to Git)
- ⚠️ Only use in backend (never in frontend)
- ✅ Already in `.gitignore` so it won't be committed

---

## ✅ **Next Steps:**

1. Get fresh API keys from: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/settings/api
2. Update [`.env`](.env ) with the new keys
3. Verify bucket exists: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets
4. Run test again: `python test_supabase_storage.py`
5. If test passes → Frontend uploads will work! 🎉

---

**Once you paste the correct API keys, everything will work perfectly!** 🚀
