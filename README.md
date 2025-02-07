# Identity_Inference_on_Ethereum

### Abstract

The blockchain's decentralized nature has fostered financial innovation but also enabled sophisticated fraud, including phishing scams and Ponzi schemes. Traditional fraud detection methods struggle with the scale and complexity of blockchain transactions. This paper presents a graph-based fraud detection approach that uses graph embeddings and machine learning models to classify illicit activity in Ethereum transactions in a computationally cost-effective way. 
We construct transaction graphs from XBlock data, where nodes represent  Ethereum wallets and edges denote transactions. Instead of resource-intensive Graph Neural Networks (GNNs), we employ Graph2Vec and Feather-G embeddings to convert transaction graphs into structured vectors, enabling classification with Random Forest, Support Vector Machines (SVMs) or Gradient Boosting (GB). Our results demonstrate that Feather-G embeddings significantly outperform Graph2Vec, preserving critical transaction patterns. Among various classifiers, Gradient Boosting with Feather-G achieves the highest accuracy (93.9\%) and F1-score (93.6\%), making it the most effective fraud detection model.
To facilitate real-world application, we integrate our model into an interactive web tool that enables real-time fraud assessment using the Etherscan API. Our findings highlight the potential of graph embedding-based machine learning in blockchain security while balancing accuracy, interpretability, and computational efficiency.

### Requirements

The codebase is implemented in Python 3.7.10.
```

pickle        3.10.0
networkx      2.5
karateclub    1.2.2
scikit-learn  0.23.2
```

```
pip install -r requirements.txt
```

### Dataset

We collect data from XBlock, which is one of the blockchain data platforms in the academic community. XBlock is a data sets sharing platform designed to facilitate the development of blockchain research. We use a second-order transaction network of phishing nodes dataset in XBlock transaction-dataset. This dataset contains 1,660 verified phishing addresses reported in the list before October 17th, 2019, 200 verified ponzi-scheme addresses and randomly chosen 1,700 normal addresses. According to the list of the addresses, they crawled the transaction network of each address using the API provided by Etherscan. The transaction network consists of the first-order transaction network that consists of transactions between the target address and their neighbors and the second-order transaction network that consists of transactions between the first-order network and their neighbors. Each transaction contains sender, receiver, amount of transaction value, and timestamp of the transaction.

The datasets are available in [[here]](http://xblock.pro/tx/).

### How to train and perform inference


```
$ python train.py # Train and evaluate models
```

```
$ python test_classify.py --wallet_address <WALLET_ADDRESS> --embedding <EMBEDDING_METHOD> --model <MODEL_NAME> # Classify a wallet address
```

In the `api/data/graphs` path, ensure the required graph datasets are available before training the models.

- Normal first-order nodes
- Normal second-order nodes
- Phishing first-order nodes
- Phishing second-order nodes

### Option

```
--graph       STR   Order of transaction graphs(first, second).           Default is 'first'
--embedding   STR   Embedding algorithms(Feather-G, Graph2Vec, GL2Vec).   Default is 'Feather-G'.
--classifier  STR   Classifier(SVM, MLP, RF, GB).                         Default is 'GB'.
```

### Example

The following command trains and evaluates models:

```
$ python train.py
```

The following command classifies a phishing node with Feather-G and RandomForest:

```
$ python test_classify.py --wallet_address 0x123456789abcdef --embedding "Feather-G" --model "RF"
```

### Web App

For Information on how to locally run or deploy the web app, please refer to the `APP_README.md` file.
```
