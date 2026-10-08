#include "test_framework.hpp"
#include "msa/tree/distance_matrix.hpp"
#include "msa/tree/guide_tree.hpp"
#include "msa/tree/upgma.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"

#include <string>
#include <vector>
#include <algorithm>

namespace {

bool verifyResidueConservation(std::string_view raw, std::string_view aligned) {
    std::string stripped;
    stripped.reserve(aligned.size());
    for (char c : aligned) {
        if (c != '-') stripped.push_back(c);
    }
    return stripped == raw;
}

} // anonymous namespace

// =============================================================================
// Milestone 4: Tree, Distance Matrix, and Progressive Pipeline Tests
// =============================================================================

TEST_CASE("DistanceMatrix - Normalized Distance Formula & Boundaries") {
    using namespace msa::tree;

    // Self distance is 0.0
    double d_self = DistanceMatrix::computeNormalizedDistance(100, 100, 100);
    CHECK_NEAR(d_self, 0.0, 1e-9);

    // Standard formula: 1.0 - 60 / max(100, 80) = 1.0 - 0.60 = 0.40
    double d_norm = DistanceMatrix::computeNormalizedDistance(60, 100, 80);
    CHECK_NEAR(d_norm, 0.40, 1e-6);

    // Highly divergent clamped to 2.0
    double d_neg = DistanceMatrix::computeNormalizedDistance(-200, 100, 100);
    CHECK(d_neg <= 2.0);
    CHECK_NEAR(d_neg, 2.0, 1e-6);

    // Negative max_self handled safely
    double d_zero_self = DistanceMatrix::computeNormalizedDistance(-10, -5, -20);
    CHECK_NEAR(d_zero_self, 1.0, 1e-6);
}

TEST_CASE("UPGMA - 3 Sequences Guide Tree Structure") {
    using namespace msa::tree;
    using namespace msa::core;

    std::vector<Sequence> seqs = {
        Sequence("s1", "HEAGAWGHEE"),
        Sequence("s2", "HEAGVWGHEE"), // 1 mismatch vs s1
        Sequence("s3", "PAWHEAE")      // distant
    };

    auto tree = UPGMA::buildTree(seqs);
    CHECK_EQ(tree.numLeaves(), 3ULL);
    CHECK(!tree.empty());

    const auto* root = tree.root();
    CHECK(root != nullptr);
    CHECK(!root->is_leaf);
    CHECK_EQ(root->clade_size, 3ULL);

    // Closest pair s1 and s2 must be clustered together in one of the child branches
    bool s1_s2_clustered = false;
    if (root->left && !root->left->is_leaf) {
        const auto* cl = root->left.get();
        if ((cl->left->name == "s1" && cl->right->name == "s2") ||
            (cl->left->name == "s2" && cl->right->name == "s1")) {
            s1_s2_clustered = true;
        }
    } else if (root->right && !root->right->is_leaf) {
        const auto* cr = root->right.get();
        if ((cr->left->name == "s1" && cr->right->name == "s2") ||
            (cr->left->name == "s2" && cr->right->name == "s1")) {
            s1_s2_clustered = true;
        }
    }
    CHECK(s1_s2_clustered);

    // Ultrametric property: root height > internal node height
    double child_height = root->left->is_leaf ? root->right->height : root->left->height;
    CHECK(root->height > child_height);
}

TEST_CASE("UPGMA - Deterministic Tie-Breaking") {
    using namespace msa::tree;

    // 4 elements with symmetric, equidistant matrix
    DistanceMatrix dm(4);
    for (size_t i = 0; i < 4; ++i) {
        for (size_t j = i + 1; j < 4; ++j) {
            dm.set(i, j, 0.50);
        }
    }

    std::vector<std::string> names = {"A", "B", "C", "D"};
    auto tree1 = UPGMA::buildTree(dm, names);
    auto tree2 = UPGMA::buildTree(dm, names);

    // Consistent and deterministic
    CHECK_EQ(tree1.root()->clade_size, 4ULL);
    CHECK_EQ(tree2.root()->clade_size, 4ULL);
    CHECK_NEAR(tree1.root()->height, tree2.root()->height, 1e-9);
}

TEST_CASE("ProgressiveAlignment - End-to-End Pipeline on 5 Sequences") {
    using namespace msa::tree;
    using namespace msa::core;

    std::vector<Sequence> seqs = {
        Sequence("alpha_human", "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH"),
        Sequence("alpha_chimp", "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH"),
        Sequence("beta_human",  "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLST"),
        Sequence("gamma_human", "GHFTEEDKATITSLWGKVNVEDAGGETLGRLLVVYPWTQRFFDSFGNLSS"),
        Sequence("myoglobin",   "GLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLK")
    };

    auto tree = UPGMA::buildTree(seqs);
    auto msa_profile = tree.progressiveAlign(seqs);

    // Acceptance Criterion 1: All sequences present
    CHECK_EQ(msa_profile.numSequences(), 5ULL);

    size_t msa_len = msa_profile.length();
    CHECK(msa_len >= 50ULL);

    // Acceptance Criterion 2: Equal length across all sequences in output
    for (size_t i = 0; i < msa_profile.numSequences(); ++i) {
        const std::string& aligned_seq = msa_profile.getAlignedSequence(i);
        CHECK_EQ(aligned_seq.length(), msa_len);

        // Acceptance Criterion 3: Residue conservation (no introduced/lost amino acids)
        CHECK(verifyResidueConservation(seqs[i].seq(), aligned_seq));
    }

    // Verify consensus sequence is well-formed
    std::string consensus = msa_profile.consensusSequence();
    CHECK_EQ(consensus.length(), msa_len);
}

TEST_CASE("ProgressiveAlignment - Boundary Cases: 1 and 2 Sequences") {
    using namespace msa::tree;
    using namespace msa::core;

    // 1 Sequence
    std::vector<Sequence> single = {Sequence("single", "HEAGAWGHEE")};
    auto tree_single = UPGMA::buildTree(single);
    auto prof_single = tree_single.progressiveAlign(single);
    CHECK_EQ(prof_single.numSequences(), 1ULL);
    CHECK_EQ(prof_single.getAlignedSequence(0), "HEAGAWGHEE");

    // 2 Sequences
    std::vector<Sequence> pair = {
        Sequence("p1", "HEAGAWGHEE"),
        Sequence("p2", "HEAGWGHEE")
    };
    auto tree_pair = UPGMA::buildTree(pair);
    auto prof_pair = tree_pair.progressiveAlign(pair);
    CHECK_EQ(prof_pair.numSequences(), 2ULL);
    CHECK_EQ(prof_pair.getAlignedSequence(0).length(), 10ULL);
    CHECK_EQ(prof_pair.getAlignedSequence(1).length(), 10ULL);
    CHECK(verifyResidueConservation(pair[0].seq(), prof_pair.getAlignedSequence(0)));
    CHECK(verifyResidueConservation(pair[1].seq(), prof_pair.getAlignedSequence(1)));
}

TEST_CASE("GuideTree - toNewick and toJson Serialization") {
    using namespace msa::tree;
    using namespace msa::core;

    std::vector<Sequence> seqs = {
        Sequence("seqA", "HEAGAWGHEE"),
        Sequence("seqB", "HEAGVWGHEE"),
        Sequence("seqC", "PAWHEAE")
    };

    auto tree = UPGMA::buildTree(seqs);

    // 1. Verify Newick string
    std::string nwk = tree.toNewick();
    CHECK(!nwk.empty());
    CHECK_EQ(nwk.back(), ';');
    CHECK(nwk.find("seqA:") != std::string::npos);
    CHECK(nwk.find("seqB:") != std::string::npos);
    CHECK(nwk.find("seqC:") != std::string::npos);

    // 2. Verify JSON string
    std::string json_str = tree.toJson();
    CHECK(!json_str.empty());
    CHECK(json_str.find("\"name\": \"seqA\"") != std::string::npos);
    CHECK(json_str.find("\"name\": \"seqB\"") != std::string::npos);
    CHECK(json_str.find("\"name\": \"seqC\"") != std::string::npos);
    CHECK(json_str.find("\"clade_size\": 3") != std::string::npos);
    CHECK(json_str.find("\"is_leaf\": true") != std::string::npos);
    CHECK(json_str.find("\"is_leaf\": false") != std::string::npos);
    CHECK(json_str.find("\"branch_length\":") != std::string::npos);

    // 3. File write and read
    std::filesystem::path tmp_nwk = std::filesystem::temp_directory_path() / "test_export.nwk";
    std::filesystem::path tmp_json = std::filesystem::temp_directory_path() / "test_export.json";
    tree.writeNewick(tmp_nwk);
    tree.writeJson(tmp_json);
    CHECK(std::filesystem::exists(tmp_nwk));
    CHECK(std::filesystem::exists(tmp_json));
    CHECK(std::filesystem::file_size(tmp_nwk) > 10);
    CHECK(std::filesystem::file_size(tmp_json) > 50);
    std::filesystem::remove(tmp_nwk);
    std::filesystem::remove(tmp_json);
}
