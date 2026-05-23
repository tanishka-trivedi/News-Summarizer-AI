# 📰 News Summarizer (Extractive + Abstractive NLP)

A complete NLP-based news summarization system that implements both **Extractive (TF-IDF)** and **Abstractive (Transformer-based)** approaches. The project demonstrates the transition from traditional NLP techniques to modern deep learning methods.

---

## 🚀 Overview

This project allows users to:
- Input a news article via **text or URL**
- Generate summaries using:
  - Extractive summarization (TF-IDF)
  - Abstractive summarization (Transformer - BART)
- Compare outputs from both approaches

---

## ✨ Features

- 🔹 Extractive summarization using TF-IDF
- 🔹 Sentence scoring and ranking
- 🔹 Text preprocessing and cleaning
- 🔹 Sentence filtering (removing noise)
- 🔹 Redundancy removal using cosine similarity
- 🔹 Abstractive summarization using Transformer models
- 🔹 Chunking for handling long articles
- 🔹 URL-based article extraction using `newspaper3k`

---

## 🧠 Methodology

### 🔹 Extractive Summarization

1. Tokenize text into sentences
2. Clean and preprocess text
3. Convert sentences into TF-IDF vectors
4. Score sentences based on importance
5. Apply normalization and length weighting
6. Remove redundant sentences
7. Select top-ranked sentences as summary

---

### 🔹 Abstractive Summarization

- Uses pretrained Transformer model: `facebook/bart-large-cnn`
- Generates new sentences instead of extracting existing ones
- Handles long text using chunking

---

## 🛠️ Tech Stack

- Python
- NLTK
- Scikit-learn
- Transformers (HuggingFace)
- PyTorch
- Newspaper3k

---

## 📂 Project Structure

```
news-summarizer/
│
├── main.py
├── extractive.py
├── abstractive.py
├── utils.py
└── README.md
```

---

## ⚙️ Installation

```bash
pip install nltk scikit-learn transformers torch newspaper3k
```

Download NLTK resources:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

---

## ▶️ Usage

### 🔹 Run the Project

```bash
python main.py
```

---

### 🔹 Example (Text Input)

```python
text = "Your article here..."
summary = summarizer(text, 3)
print(summary)
```

---

### 🔹 Example (URL Input)

```python
url = "https://example.com/news"
text = getArticle(url)

summary = summarizer(text, 3)
print(summary)
```

---

### 🔹 Abstractive Summary

```python
summary = abstractive_summarizer(text)
print(summary)
```

---

## 📊 Comparison

| Feature               | Extractive         | Abstractive        |
|-----------------------|--------------------|--------------------|
| Method                | TF-IDF             | Transformer        |
| Output                | Existing sentences | Generated text     |
| Speed                 | Fast               | Slower             |
| Readability           | Moderate           | High               |
| Context Understanding | Low                | High               |

---

## ⚠️ Limitations

**Extractive summarization:**
- Does not understand semantic meaning
- May produce repetitive summaries

**Abstractive summarization:**
- Computationally expensive
- Limited input length (requires chunking)
- May generate slightly inaccurate summaries

---

## 🚀 Future Improvements

- Add Streamlit UI
- Deploy the project online
- Add ROUGE score evaluation
- Improve semantic redundancy removal

---

## 💼 Resume Highlight

> Developed an NLP-based news summarization system using both TF-IDF and Transformer models, incorporating real-time article extraction and comparative analysis between extractive and abstractive approaches.

---

## 👤 Author

Your Name  
GitHub: [https://github.com/your-username](https://github.com/your-username)
