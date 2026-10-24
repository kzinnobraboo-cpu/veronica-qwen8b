<div align="center">

# ✦ VERONICA

**Uma IA local com presença de terminal. Criada por Neo, um dev solo.**

`Qwen` · `Ollama` · `Python` · `100% local`

</div>

```text
██╗   ██╗███████╗██████╗  ██████╗ ███╗   ██╗██╗ ██████╗ █████╗
██║   ██║██╔════╝██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██╔══██╗
██║   ██║█████╗  ██████╔╝██║   ██║██╔██╗ ██║██║██║     ███████║
╚██╗ ██╔╝██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║██║██║     ██╔══██║
 ╚████╔╝ ███████╗██║  ██║╚██████╔╝██║ ╚████║██║╚██████╗██║  ██║
  ╚═══╝  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═╝
```

Veronica é um chat para terminal com respostas em streaming, contexto de conversa, gradiente ANSI e interface inspirada na estética limpa de ferramentas como OpenCode. A interface não aplica filtros de conteúdo próprios. As respostas dependem do modelo escolhido.

## Instalação

Requer Python 3.10+ e [Ollama](https://ollama.com/download).

```bash
ollama pull qwen3:8b
ollama serve
```

Em outro terminal:

```bash
python3 veronica.py
```

O modelo padrão é `qwen3:8b`. Você pode trocar para outro modelo instalado com `--model nome:tag` ou `VERONICA_MODEL=nome:tag`.

## Uso

```bash
python3 veronica.py "Quem é seu dono?"
python3 veronica.py --model qwen3:8b
VERONICA_MODEL=qwen3:8b python3 veronica.py
```

| Comando | Ação |
| --- | --- |
| `/ajuda` | Lista comandos |
| `/limpar` | Apaga o contexto da sessão |
| `/modelo` | Mostra o modelo em uso |
| `/sair` | Fecha o chat |

`--url` permite apontar para outro servidor Ollama; o padrão é `http://127.0.0.1:11434`. `--no-color` e `NO_COLOR=1` desativam cores. O histórico fica só na memória da sessão e não é salvo em disco.

## Identidade

Ao perguntar quem criou a Veronica, ela responde: **Neo, um dev solo**. O prompt de identidade também pede respostas diretas e honestas, sem fingir executar ações externas.

## Licença

MIT. Veja [LICENSE](LICENSE).
