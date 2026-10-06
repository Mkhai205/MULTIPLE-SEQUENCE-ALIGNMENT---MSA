#include "test_framework.hpp"
#include "msa/parallel/wavefront.hpp"
#include "msa/parallel/tree_scheduler.hpp"
#include "msa/tree/distance_matrix.hpp"
#include "msa/tree/upgma.hpp"
#include "msa/tree/guide_tree.hpp"
#include "msa/align/needleman_wunsch.hpp"
#include "msa/align/hirschberg.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

#include <string>
#include <vector>
#include <cmath>
#include <algorithm>

using namespace msa;

namespace {

bool verifyResidues(std::string_view raw, std::string_view aligned) {
    std::string stripped;
    stripped.reserve(aligned.size());
    for (char c : aligned) {
        if (c != '-') stripped.push_back(c);
    }
    return stripped == raw;
}

} // anonymous namespace

TEST_CASE("Parallel - Wavefront Score Matches Needleman-Wunsch Exactly") {
    core::ScoreModel model(-10, -1);
    const auto& matrix = core::Blosum62::instance();
    align::NeedlemanWunsch nw(model, matrix);

    std::vector<std::pair<std::string, std::string>> test_pairs = {
        {"HEAGAWGHEE", "PAWHEAE"},
        {"ACDEFGHIKLMNPQRSTVWY", "ACDEFGHIKLMNPQRSTVWY"},
        {"HEAGAWGHEE", "HEAGAWGHEE"},
        {"MKFLILLFNILCLFPVLAADNHGVGPQGASCELID", "MKFLILLFNILCLFPVLAADNHGVGPQGASCELID"},
        {"MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGE", "MKTFIFLALLGAAVAFPVDDDDKIVGGYTCAANSIPYQVSL"},
        {"ALAAAAA", "AAAAAAAA"},
        {"CDE", "FGHIJKL"},
        {"W", "W"},
        {"WW", "W"}
    };

    for (const auto& [s1, s2] : test_pairs) {
        auto nw_res = nw.align(s1, s2);
        // Test with default threshold (256) and force-parallel threshold (1)
        int score_def = parallel::wavefront_gotoh_score(s1, s2, model, matrix, 256);
        int score_low = parallel::wavefront_gotoh_score(s1, s2, model, matrix, 1);

        CHECK_EQ(nw_res.score, score_def);
        CHECK_EQ(nw_res.score, score_low);

        // Also test wavefront alignment traceback
        auto wf_res = parallel::wavefront_gotoh_align(s1, s2, model, matrix, 1);
        CHECK_EQ(nw_res.score, wf_res.score);
        CHECK_EQ(wf_res.aligned_seq1.length(), wf_res.aligned_seq2.length());

        // Validate residue content
        CHECK(verifyResidues(s1, wf_res.aligned_seq1));
        CHECK(verifyResidues(s2, wf_res.aligned_seq2));

        // Validate no column is double gap
        for (size_t k = 0; k < wf_res.aligned_seq1.length(); ++k) {
            CHECK(!(wf_res.aligned_seq1[k] == '-' && wf_res.aligned_seq2[k] == '-'));
        }
    }
}

TEST_CASE("Parallel - Distance Matrix Equivalence (Sequential vs Parallel)") {
    core::ScoreModel model(-10, -1);
    const auto& matrix = core::Blosum62::instance();

    std::vector<core::Sequence> seqs = {
        core::Sequence("seq1", "MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGEEHFKGLVLIAFSQYLQQCPFDEHVKLVNELTEFAKTCVAD"),
        core::Sequence("seq2", "MKFLILLFNILCLFPVLAADNHGVGPQGASCEELIDMNKDTVLEFLAKVKGNEKLYEAKCEELMNKKVLDAIKEKGI"),
        core::Sequence("seq3", "MKTFIFLALLGAAVAFPVDDDDKIVGGYTCAANSIPYQVSLNSGSHFCGGSLINSQWVVSAAHCYKSRIQVRLGEHNINV"),
        core::Sequence("seq4", "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNAL"),
        core::Sequence("seq5", "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNL"),
        core::Sequence("seq6", "MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGEEHFKGLVLIAFSQYLQQCPFDEHVKLVNELTEFAKTCVAD")
    };

    auto dist_seq = tree::DistanceMatrix::compute(seqs, model, matrix, false);
    auto dist_par = tree::DistanceMatrix::compute(seqs, model, matrix, true);

    CHECK_EQ(dist_seq.size(), dist_par.size());
    CHECK_EQ(dist_seq.size(), seqs.size());

    for (size_t i = 0; i < seqs.size(); ++i) {
        for (size_t j = 0; j < seqs.size(); ++j) {
            double diff = std::abs(dist_seq.get(i, j) - dist_par.get(i, j));
            CHECK_NEAR(diff, 0.0, 1e-9);
        }
    }
}

TEST_CASE("Parallel - Progressive Alignment Tree Scheduler Equivalence") {
    core::ScoreModel model(-10, -1);
    const auto& matrix = core::Blosum62::instance();

    std::vector<core::Sequence> seqs = {
        core::Sequence("s1", "HEAGAWGHEE"),
        core::Sequence("s2", "PAWHEAE"),
        core::Sequence("s3", "HEAWGHEE"),
        core::Sequence("s4", "PAWHE"),
        core::Sequence("s5", "HEAGAW")
    };

    std::vector<std::string> names;
    for (const auto& s : seqs) names.push_back(s.id());

    auto dist = tree::DistanceMatrix::compute(seqs, model, matrix, true);
    auto guide_tree = tree::UPGMA::buildTree(dist, names);

    // Sequential progressive align
    auto seq_prof = guide_tree.progressiveAlign(seqs, model, matrix);

    // Parallel progressive align
    auto par_prof = parallel::parallel_progressive_align(guide_tree, seqs, model, matrix, 4);

    CHECK_EQ(seq_prof.numSequences(), par_prof.numSequences());
    CHECK_EQ(seq_prof.length(), par_prof.length());

    for (size_t i = 0; i < seq_prof.numSequences(); ++i) {
        CHECK_EQ(seq_prof.getAlignedSequence(i), par_prof.getAlignedSequence(i));
    }
}

TEST_CASE("Parallel - Tree Scheduler with Larger Dataset") {
    core::ScoreModel model(-10, -1);
    const auto& matrix = core::Blosum62::instance();

    std::vector<core::Sequence> seqs = {
        core::Sequence("A", "MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGE"),
        core::Sequence("B", "MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGEEHFK"),
        core::Sequence("C", "MKWVTFISLLLLFSSAYSRGVFRRDTHKS"),
        core::Sequence("D", "MKTFIFLALLGAAVAFPVDDDDKIVGGYTCAANSIPYQVSL"),
        core::Sequence("E", "MKTFIFLALLGAAVAFPVDDDDKIVGGYTCAANSIPYQVSLNSGSHFC"),
        core::Sequence("F", "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQR"),
        core::Sequence("G", "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLST"),
        core::Sequence("H", "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTT")
    };

    std::vector<std::string> names;
    for (const auto& s : seqs) names.push_back(s.id());

    auto dist = tree::DistanceMatrix::compute(seqs, model, matrix, true);
    auto guide_tree = tree::UPGMA::buildTree(dist, names);

    auto seq_prof = guide_tree.progressiveAlign(seqs, model, matrix);
    auto par_prof = parallel::parallel_progressive_align(guide_tree, seqs, model, matrix, 2);

    CHECK_EQ(par_prof.numSequences(), seqs.size());
    CHECK(par_prof.length() >= 40ULL);

    // Validate that each aligned sequence retains original residues matching by ID
    for (size_t i = 0; i < par_prof.numSequences(); ++i) {
        std::string id = par_prof.getSequenceId(i);
        const std::string& aligned = par_prof.getAlignedSequence(i);
        auto it = std::find_if(seqs.begin(), seqs.end(), [&](const core::Sequence& s) { return s.id() == id; });
        CHECK(it != seqs.end());
        if (it != seqs.end()) {
            CHECK(verifyResidues(it->seq(), aligned));
        }
    }
}
