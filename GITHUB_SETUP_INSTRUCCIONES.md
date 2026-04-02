# 📤 Subir ColdTemplar a GitHub - Guía Paso a Paso

¡Tu repositorio local está listo! Ahora necesitas crearlo en GitHub y hacer push.

---

## 📋 Requisitos Previos

✅ **Cuenta GitHub activa** - Si no tienes, créala en https://github.com/join  
✅ **Git configurado** - Ya hecho: `c0ldtemplar`  
✅ **Repositorio local** - Ya inicializado con primer commit  

---

## 🚀 Opción 1: HTTPS (Más Fácil - Recomendado para principiantes)

### Paso 1: Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Rellena los datos:
   - **Repository name:** `ColdTemplar-Labs`
   - **Description:** `Asistente de voz inteligente en español con IA local`
   - **Public** (para que otros puedan verlo)
   - **NO marques** "Initialize this repository with:"
3. Haz click en **"Create repository"**

### Paso 2: Copiar la URL

En la pantalla siguiente, verás instrucciones. Copia la URL HTTPS que se vea así:
```
https://github.com/TU_USUARIO/ColdTemplar-Labs.git
```

### Paso 3: Ejecutar en tu Terminal

Reemplaza `TU_USUARIO` con tu usuario real de GitHub:

```bash
cd ~/ColdTemplar-Labs

# Agregar repositorio remoto
git remote add origin https://github.com/TU_USUARIO/ColdTemplar-Labs.git

# Renombrar rama a 'main' (estándar moderno)
git branch -M main

# Subir al repositorio remoto
git push -u origin main
```

### Paso 4: Ingresar Credenciales

GitHub te pedirá:
- **Username:** Tu usuario de GitHub
- **Password:** Tu token de acceso (ver nota abajo)

💡 **Nota sobre Token:** Si no funciona con tu contraseña:
1. Ve a https://github.com/settings/tokens
2. Crea un **Personal Access Token** (Fine-grained)
3. Dale permisos a `Contents` y `Metadata`
4. Usa ese token como contraseña

---

## 🔐 Opción 2: SSH (Más Seguro - Para usuarios avanzados)

### Paso 1: Generar Clave SSH (si no existe)

```bash
ssh-keygen -t ed25519 -C "tu.email@example.com"
# Presiona Enter 3 veces para defaults
```

### Paso 2: Agregar Clave a GitHub

```bash
# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub
```

1. Ve a https://github.com/settings/keys
2. Haz click en **"New SSH key"**
3. Pega el contenido de la clave
4. Guarda

### Paso 3: Crear Repositorio en GitHub

Igual a Opción 1, Paso 1.

### Paso 4: Ejecutar en tu Terminal

```bash
cd ~/ColdTemplar-Labs

# Agregar repositorio remoto (SSH)
git remote add origin git@github.com:TU_USUARIO/ColdTemplar-Labs.git

# Renombrar rama
git branch -M main

# Subir
git push -u origin main
```

---

## ✅ Verificar que Todo Funcionó

```bash
cd ~/ColdTemplar-Labs

# Ver remoto configurado
git remote -v

# Ver ramas
git branch -a

# Ver commits
git log --oneline
```

**Salida esperada:**
```
origin  https://github.com/TU_USUARIO/ColdTemplar-Labs.git (fetch)
origin  https://github.com/TU_USUARIO/ColdTemplar-Labs.git (push)
* main
  remotes/origin/main
782b222 (HEAD -> main, origin/main) Initial commit: ColdTemplar Voice Assistant v2.0
```

---

## 🎉 ¡Listo!

Tu repositorio está en línea. Puedes ver en: https://github.com/TU_USUARIO/ColdTemplar-Labs

---

## 📝 Comandos Útiles Después

### Hacer cambios y subir

```bash
# Editar archivo
# ...cambios...

# Ver cambios
git status

# Preparar cambios
git add .

# Hacer commit
git commit -m "Descripción del cambio"

# Subir a GitHub
git push
```

### Ver tu repositorio remoto

```bash
git remote -v
```

### Cambiar URL remota (si cometiste error)

```bash
git remote set-url origin https://github.com/TU_USUARIO/ColdTemplar-Labs.git
# o
git remote set-url origin git@github.com:TU_USUARIO/ColdTemplar-Labs.git
```

### Verificar estado

```bash
git status
git log --oneline -5
git branch -a
```

---

## 🆘 Troubleshooting

### "fatal: remote origin already exists"

```bash
# Si ya existe, quítalo y vuelve a agregarlo
git remote remove origin
git remote add origin [URL]
git push -u origin main
```

### "Permission denied (publickey)"

- Verifica que tienes SSH key en GitHub (opción SSH)
- O usa HTTPS en lugar de SSH

### "failed to authenticate"

- Verifica tu token/contraseña
- Si usas token, NO uses como "Password" en HTTPS - usa Credentials Manager

### "Rama incorrecta"

```bash
# Ver qué rama estás
git branch

# Cambiar a main si estás en master
git checkout -b main --track origin/main
git push -u origin main
```

---

## 📚 Recursos Útiles

- [Documentación de GitHub](https://docs.github.com/es)
- [Git Cheat Sheet](https://github.github.com/training-kit/downloads/es_ES/github-git-cheat-sheet.pdf)
- [Tutorial Interactivo de Git](https://learngitbranching.js.org/)

---

## 🎯 Próximos Pasos (Después de Subir)

1. ✅ Subir a GitHub
2. 📌 Crear archivo `.github/workflows/` para CI/CD (opcional)
3. 📝 Agregar Issues y Pull Request Templates
4. 🏷️ Crear Tags/Releases para versiones
5. 🔗 Compartir link con la comunidad

---

## 💡 Bonus: Colaboradores

Si quieres que otros trabajen en el proyecto:

```bash
# En GitHub, ve a Settings > Collaborators
# Agrega usuarios por email
```

---

**¡Felicidades! Tu proyecto está en GitHub.** 🎉

