# Auto Key Presser - README

## English (EN)

### Overview
Auto Key Presser is a utility application that automatically presses specified keys at defined intervals. It's useful for gaming, automation, or any scenario where repetitive key presses are needed.

### Key Features
- Add/remove keys with custom intervals
- Toggle active/inactive for each key
- Global hotkeys (F7=Start, F8=Stop)
- Multi-language support
- Persistent configuration

### How to Use
1. **Adding Keys**:
   - Enter the key in the "Key" field (e.g., 'z', 'space', 'f1')
   - Enter the interval in milliseconds (1000ms = 1 second)
   - Click "Add"

2. **Removing Keys**:
   - Select a key in the list
   - Click "Remove"

3. **Toggling Active/Inactive**:
   - Double-click on the checkmark (✓/✗) in the "Active" column

4. **Starting/Stopping**:
   - Click "Start" to begin auto-pressing active keys
   - Click "Stop" to halt the process
   - Or use hotkeys: F7 (Start), F8 (Stop)

### Key Behavior
Each key operates independently with its own timer. This means:
- Different keys can have different intervals
- Keys will press at their scheduled times without waiting for others
- The app manages key presses efficiently to prevent conflicts

### Adding New Languages
1. Create a new text file (e.g., "fr.txt" for French)
2. Add all required key-value pairs (copy structure from existing language files)
3. Edit the values with your translations
4. Add the language to locales.json:
```json
{
  "languages": [
    ...,
    {
      "code": "fr",
      "name": "Français",
      "file": "fr.txt"
    }
  ]
}
```

## Português (PT)

### Visão Geral
O Auto Key Presser é um aplicativo utilitário que pressiona teclas especificadas em intervalos definidos. É útil para jogos, automação ou qualquer cenário onde pressionamentos repetitivos de teclas são necessários.

### Principais Recursos
- Adicionar/remover teclas com intervalos personalizados
- Alternar ativo/inativo para cada tecla
- Atalhos globais (F7=Iniciar, F8=Parar)
- Suporte a múltiplos idiomas
- Configuração persistente

### Como Usar
1. **Adicionando Teclas**:
   - Digite a tecla no campo "Tecla" (ex: 'z', 'space', 'f1')
   - Digite o intervalo em milissegundos (1000ms = 1 segundo)
   - Clique em "Adicionar"

2. **Removendo Teclas**:
   - Selecione uma tecla na lista
   - Clique em "Remover"

3. **Alternando Ativo/Inativo**:
   - Clique duas vezes no símbolo (✓/✗) na coluna "Ativo"

4. **Iniciando/Parando**:
   - Clique em "Iniciar" para começar o pressionamento automático
   - Clique em "Parar" para interromper o processo
   - Ou use os atalhos: F7 (Iniciar), F8 (Parar)

### Comportamento das Teclas
Cada tecla opera independentemente com seu próprio temporizador. Isso significa:
- Teclas diferentes podem ter intervalos diferentes
- As teclas serão pressionadas em seus horários agendados sem esperar pelas outras
- O aplicativo gerencia os pressionamentos de forma eficiente para evitar conflitos

### Adicionando Novos Idiomas
1. Crie um novo arquivo de texto (ex: "fr.txt" para Francês)
2. Adicione todos os pares chave-valor necessários (copie a estrutura dos arquivos existentes)
3. Edite os valores com suas traduções
4. Adicione o idioma ao locales.json:
```json
{
  "languages": [
    ...,
    {
      "code": "fr",
      "name": "Français",
      "file": "fr.txt"
    }
  ]
}
```

## Español (ESP)

### Resumen
Auto Key Presser es una aplicación utilitaria que presiona teclas específicas en intervalos definidos. Es útil para juegos, automatización o cualquier escenario donde se necesiten pulsaciones repetitivas de teclas.

### Características Principales
- Añadir/eliminar teclas con intervalos personalizados
- Alternar activo/inactivo para cada tecla
- Atajos globales (F7=Iniciar, F8=Detener)
- Soporte para múltiples idiomas
- Configuración persistente

### Cómo Usar
1. **Añadir Teclas**:
   - Ingrese la tecla en el campo "Tecla" (ej: 'z', 'space', 'f1')
   - Ingrese el intervalo en milisegundos (1000ms = 1 segundo)
   - Haga clic en "Agregar"

2. **Eliminar Teclas**:
   - Seleccione una tecla en la lista
   - Haga clic en "Eliminar"

3. **Alternar Activo/Inactivo**:
   - Haga doble clic en el símbolo (✓/✗) en la columna "Activo"

4. **Iniciar/Detener**:
   - Haga clic en "Iniciar" para comenzar el presionado automático
   - Haga clic en "Detener" para interrumpir el proceso
   - O use los atajos: F7 (Iniciar), F8 (Detener)

### Comportamiento de las Teclas
Cada tecla opera independientemente con su propio temporizador. Esto significa:
- Diferentes teclas pueden tener diferentes intervalos
- Las teclas se presionarán en sus tiempos programados sin esperar a otras
- La aplicación gestiona las pulsaciones eficientemente para prevenir conflictos

### Añadir Nuevos Idiomas
1. Cree un nuevo archivo de texto (ej: "fr.txt" para Francés)
2. Añada todos los pares clave-valor necesarios (copie la estructura de archivos existentes)
3. Edite los valores con sus traducciones
4. Añada el idioma a locales.json:
```json
{
  "languages": [
    ...,
    {
      "code": "fr",
      "name": "Français",
      "file": "fr.txt"
    }
  ]
}
```
