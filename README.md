# Bar-o: Análise de Terrenos Rurais com Drone (offline)

Software local (sem internet após instalação) para pequenos produtores rurais (até 50 hectares).

Ele transforma fotos de drone em:
- mapa visual do terreno (ortomosaico simples),
- planta rural inteligente por zonas,
- relatório profissional em PDF,
- e modelo 3D opcional (Premium).

---

## ✅ Jeito mais fácil (para quem é leigo)

### Windows
1. Instale **Python 3.10+** (marque a opção `Add Python to PATH` na instalação).
2. Baixe/extraia a pasta do projeto.
3. Dê duplo clique em **`start_windows.bat`**.
4. Aguarde a instalação automática.
5. A tela do sistema abrirá sozinha.

### Linux/macOS
1. Instale **Python 3.10+**.
2. Abra o terminal na pasta do projeto.
3. Rode:
   ```bash
   ./start_linux.sh
   ```
4. Aguarde a instalação automática.
5. A tela do sistema abrirá sozinha.

> Esses scripts usam o arquivo `setup_local.py`, que cria ambiente virtual, instala bibliotecas e executa o app.

---

## Instalação manual (se preferir)

1. Abra terminal na pasta do projeto.
2. Crie ambiente virtual:
   ```bash
   python -m venv .venv
   ```
3. Ative:
   - Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## Como rodar

```bash
python main.py
```

---

## Como usar (passo a passo)

1. **Cadastro**
   - Preencha nome do cliente, propriedade, cidade, data e observações.

2. **Upload de imagens do drone**
   - Clique em **"1) Selecionar pasta de imagens"** e escolha a pasta com as fotos.

3. **Criar mapa visual**
   - Clique em **"2) Gerar mapa (ortomosaico)"**.
   - O sistema tenta unir as imagens automaticamente.
   - Se não conseguir unir perfeitamente, ele usa um fallback simples para garantir resultado.

4. **Desenhar limite do terreno**
   - Clique sobre o mapa para marcar os pontos do terreno.
   - Com 3 ou mais pontos, o polígono fica definido visualmente.
   - Se errar, use **"3) Limpar pontos do polígono"**.

5. **Gerar relatório PDF**
   - Clique em **"4) Gerar relatório PDF"**.
   - O sistema gera: área total (m² e ha), diagnóstico, sugestões, mapa e planta por zonas.

6. **Modo Premium (opcional)**
   - Clique em **"5) Premium: gerar modelo 3D"**.
   - O sistema exporta arquivos `.PLY` e `.OBJ`.

---

## Onde ficam os arquivos gerados

- `output/mosaic.png`
- `output/zone_map.png`
- `output/altitude_map.png`
- `output/relatorio_terreno.pdf`
- `models_3d/terrain_model.ply`
- `models_3d/terrain_model.obj`

---

## Estrutura do projeto

- `backend/`: regras de negócio, análise de imagem, PDF e 3D
- `frontend/`: interface Tkinter
- `images/`: armazenamento recomendado das fotos de drone
- `output/`: arquivos gerados
- `models_3d/`: modelos 3D exportados

---

## Solução de problemas (rápido)

- **Erro: "python não reconhecido"**
  - Reinstale Python e marque `Add Python to PATH`.

- **A janela não abre no Linux**
  - Instale Tkinter do sistema (ex.: `sudo apt install python3-tk`).

- **Erro ao instalar Open3D**
  - O sistema principal funciona sem 3D; tente atualizar pip e depois instalar novamente.

- **Área calculada parece diferente da real**
  - A área usa escala padrão (`0.2 m/pixel`). Para precisão maior, ajuste em `backend/terrain_analysis.py`.

---

## Dependências

As bibliotecas utilizadas são:
- `numpy`
- `opencv-python`
- `matplotlib`
- `reportlab`
- `open3d`
- `Pillow`
