import os

from main.results.functions import get_scores
from main.results.analyses import plot_scores, analyse_dmg_area_results

from toolbox.config import get_config


if __name__ == "__main__":

    model = "mgrain"
    d_type = "val"

    scores = get_scores(model, d_type)
    plt = plot_scores(scores, d_type)
    df = analyse_dmg_area_results(model, d_type)

    res_folder = get_config().results
    analyses_path = os.path.join(res_folder, model, d_type, "analyses")
    if not os.path.exists(analyses_path):
        os.mkdir(analyses_path)

    img_path = os.path.join(analyses_path, "confusion_scores.eps")
    plt.savefig(img_path)

    csv_path = os.path.join(analyses_path, "res_dmg_area.csv")
    df.to_csv(csv_path)