## Setup Weights & Biases

1. Make sure you don’t have `--tensorboard-logdir` in your launch.json (in case you’re using vscode).

2. Run `pip install wandb` in your (conda) environment.

3. Run `wandb.login()` from your (conda) env. Then copy paste your API key (terminal will prompt you and give you the URL with the key).

4. Set `—wandb-project` argument in your launch.json to `open-nllb` (or some other name).

After this your training/system metrics will get streamed to your W&B browser dashboard.