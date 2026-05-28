import os
import glob

workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(workspace, "src")

replacements = {
    'os.path.join(WORKSPACE, "train_set.csv")': 'os.path.join(WORKSPACE, "data", "processed", "train_set.csv")',
    'os.path.join(WORKSPACE, "test_set.csv")': 'os.path.join(WORKSPACE, "data", "processed", "test_set.csv")',
    'os.path.join(WORKSPACE, "results")': 'os.path.join(WORKSPACE, "outputs", "results")',
    'os.path.join(WORKSPACE, "logs")': 'os.path.join(WORKSPACE, "outputs", "logs")',
    'os.path.join(WORKSPACE, "loss_curve.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "loss_curve.png")',
    'os.path.join(WORKSPACE, "confusion_matrix.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "confusion_matrix.png")',
    'os.path.join(WORKSPACE, "hpo_validation_loss_comparison.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "hpo_validation_loss_comparison.png")',
    'os.path.join(WORKSPACE, "hpo_learning_curves.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "hpo_learning_curves.png")',
    'os.path.join(WORKSPACE, "final_model_comparison.csv")': 'os.path.join(WORKSPACE, "outputs", "reports", "final_model_comparison.csv")',
    'os.path.join(WORKSPACE, "workspace_report.md")': 'os.path.join(WORKSPACE, "outputs", "reports", "workspace_report.md")',
    'os.path.join(WORKSPACE, "academic_performance_comparison.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "academic_performance_comparison.png")',
    'os.path.join(WORKSPACE, "crisis_missed_tweets_rate.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "crisis_missed_tweets_rate.png")',
    'os.path.join(WORKSPACE, "accuracy_vs_recall_tradeoff.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "accuracy_vs_recall_tradeoff.png")',
    'os.path.join(WORKSPACE, "tweets_data_16k.csv")': 'os.path.join(WORKSPACE, "data", "raw", "tweets_data_16k.csv")',
    'os.path.join(WORKSPACE, "comprehensive_dataset_insight.md")': 'os.path.join(WORKSPACE, "outputs", "reports", "comprehensive_dataset_insight.md")',
    'os.path.join(WORKSPACE, "states")': 'os.path.join(WORKSPACE, "data", "states")',
    'os.path.join(WORKSPACE, "topic_modeling_lda.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "topic_modeling_lda.png")',
    'os.path.join(WORKSPACE, "cross_domain_generalization.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "cross_domain_generalization.png")',
    'os.path.join(WORKSPACE, "ner_location_recovery_report.md")': 'os.path.join(WORKSPACE, "outputs", "reports", "ner_location_recovery_report.md")',
    'os.path.join(WORKSPACE, "crisis_word_network.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "crisis_word_network.png")',
    'os.path.join(WORKSPACE, "sentence_length_distribution.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "sentence_length_distribution.png")',
    'os.path.join(WORKSPACE, "lexical_richness_boxplot.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "lexical_richness_boxplot.png")',
    'os.path.join(WORKSPACE, "subcategory_radar_chart.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "subcategory_radar_chart.png")',
    'os.path.join(WORKSPACE, "learning_curve_analysis.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "learning_curve_analysis.png")',
    'os.path.join(WORKSPACE, "feature_importance.png")': 'os.path.join(WORKSPACE, "outputs", "plots", "feature_importance.png")',
    'os.path.join(WORKSPACE, "error_analysis_report.md")': 'os.path.join(WORKSPACE, "outputs", "reports", "error_analysis_report.md")',
    'os.path.join(WORKSPACE, "location_deception_insight.md")': 'os.path.join(WORKSPACE, "outputs", "reports", "location_deception_insight.md")'
}

py_files = glob.glob(os.path.join(src_dir, "**", "*.py"), recursive=True)

for file in py_files:
    if file.endswith("refactor_paths.py") or file.endswith("final_pipeline.py"):
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            
    if modified:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated paths in {file}")

print("Done refactoring paths.")
