from __future__ import annotations

import math
import re
import sys
from hashlib import md5
from pathlib import Path

from src import Document, EmbeddingStore, FixedSizeChunker


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "ecommerce"
OUTPUT_PATH = ROOT / "report" / "fixed_size_benchmark_results.md"
TEXT_OUTPUT_PATH = ROOT / "ket_qua_benchmark.txt"


BENCHMARKS = [
    {
        "id": 1,
        "query": "Người mua có thể gửi yêu cầu trả hàng/hoàn tiền trong thời hạn bao lâu đối với đơn hàng thông thường?",
        "expected_files": {"return-refund-general-rules.md"},
        "metadata_filter": None,
    },
    {
        "id": 2,
        "query": "Nếu thanh toán bằng thẻ tín dụng hoặc thẻ ghi nợ thì tiền hoàn được gửi về đâu và mất bao lâu?",
        "expected_files": {"return-refund-policy.md"},
        "metadata_filter": None,
    },
    {
        "id": 3,
        "query": "Khi đã nhận hàng nhưng hàng bị lỗi, video mở kiện hàng cần đáp ứng những yêu cầu nào?",
        "expected_files": {"return-refund-evidence-guide.md"},
        "metadata_filter": None,
    },
    {
        "id": 4,
        "query": "Nếu Người mua chọn hình thức Tự sắp xếp để trả hàng thì Shopee hỗ trợ phí trả hàng như thế nào?",
        "expected_files": {"return-shipping-methods-fees.md"},
        "metadata_filter": None,
    },
    {
        "id": 5,
        "query": "Với tài liệu có audience=seller, Người bán nên làm gì khi nhận hàng hoàn nhưng sản phẩm bị hư hỏng hoặc không đúng sản phẩm của shop?",
        "expected_files": {"seller-warranty-policy.md"},
        "metadata_filter": {"audience": "seller"},
    },
]


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, parts[2].strip()


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[\wÀ-ỹ]+", text, flags=re.UNICODE)]


class KeywordHashEmbedder:
    """Deterministic lexical embedder for offline benchmark reproducibility."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self._backend_name = "keyword-hash-embedder"

    def __call__(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in tokenize(text):
            index = int(md5(token.encode("utf-8")).hexdigest(), 16) % self.dim
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def load_chunked_documents() -> list[Document]:
    chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    docs: list[Document] = []

    for path in sorted(DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata, body = parse_front_matter(text)
        for index, chunk in enumerate(chunker.chunk(body), start=1):
            chunk_metadata = {
                **metadata,
                "source_file": path.name,
                "chunk_index": index,
                "strategy": "fixed_size",
                "chunk_size": 500,
                "overlap": 50,
            }
            docs.append(
                Document(
                    id=f"{path.stem}-chunk-{index}",
                    content=chunk,
                    metadata=chunk_metadata,
                )
            )
    return docs


def summarize(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def run() -> str:
    docs = load_chunked_documents()
    store = EmbeddingStore(collection_name="fixed_size_benchmark", embedding_fn=KeywordHashEmbedder())
    store.add_documents(docs)

    lines = [
        "# FixedSizeChunker Benchmark Results",
        "",
        "- Strategy: `FixedSizeChunker(chunk_size=500, overlap=50)`",
        "- Embedding backend: local deterministic keyword-hash embedder",
        f"- Stored chunks: {store.get_collection_size()}",
        "",
        "| # | Query | Filter | Top-1 source | Top-1 score | Top-3 sources | Top-3 relevant? | Top-1 summary |",
        "|---|---|---|---|---:|---|---|---|",
    ]

    for item in BENCHMARKS:
        metadata_filter = item["metadata_filter"]
        results = store.search_with_filter(item["query"], top_k=3, metadata_filter=metadata_filter)
        top1 = results[0] if results else {"metadata": {}, "score": 0.0, "content": ""}
        top3_sources = [result["metadata"].get("source_file", "") for result in results]
        relevant = any(source in item["expected_files"] for source in top3_sources)
        filter_text = "`None`" if metadata_filter is None else f"`{metadata_filter}`"

        lines.append(
            "| {id} | {query} | {filter_text} | `{top1_source}` | {score:.4f} | {top3} | {relevant} | {summary} |".format(
                id=item["id"],
                query=item["query"],
                filter_text=filter_text,
                top1_source=top1["metadata"].get("source_file", ""),
                score=float(top1["score"]),
                top3=", ".join(f"`{source}`" for source in top3_sources),
                relevant="Yes" if relevant else "No",
                summary=summarize(top1["content"]).replace("|", "/"),
            )
        )

    output = "\n".join(lines) + "\n"
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    TEXT_OUTPUT_PATH.write_text(output, encoding="utf-8")
    return output


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(run())
