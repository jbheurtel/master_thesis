import os

from main.results.functions import get_scores, get_f1_scores
from main.results.analyses import plot_scores, analyse_dmg_area_results, plot_f1_scores

from toolbox.config import get_config


if __name__ == "__main__":

    # INPUTS
    model = "hgrain"
    d_type = "val"

    res_folder = get_config().results
    analyses_path = os.path.join(res_folder, model, d_type, "analyses")
    if not os.path.exists(analyses_path):
        os.mkdir(analyses_path)

    # PREPARATIONS
    scores = get_scores(model, d_type)
    f1_scores = get_f1_scores(scores)

    # AGGREGATORS
    plt = plot_scores(scores)
    scores_img_path = os.path.join(analyses_path, "confusion_scores.svg")
    plt.savefig(scores_img_path)

    plt_f1 = plot_f1_scores(f1_scores)
    f1_scores_img_path = os.path.join(analyses_path, "f1_scores.svg")
    plt_f1.savefig(f1_scores_img_path)

    df = analyse_dmg_area_results(model, d_type)
    csv_path = os.path.join(analyses_path, "res_dmg_area.csv")
    df.to_csv(csv_path)

    # print(df)
    # plt.show()
    # plt_f1.show()
