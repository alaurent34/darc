

######  Reidentify_Rowdata ########

□再識別フェイズ用 部分知識データ
Partial knowledge datasets of Re-identification Phase

・部分知識データはTα（T25，T50，T75，T100）があります．
  Partial knowledge data is Tα (T25, T50, T75, T100).

・このデータは，9月29日以前に作成されたデータとは抽出パターンが異なります．
また，商品IDが上位２桁しかありません．
This data differs in extraction pattern from data created before September 29.
Also, the product ID has only the upper two digits.

・再識別システムは，このデータを用いて再識別を行っています．
 → 以前のデータよりも再識別率は悪くなるはずです．
· The re-identification programs in this system is using this data.
 → The re-identification rate should be worse than the previous data.


・再識別フェイズでは，1つの匿名化データに対して，Tαを用いた再識別データFhを4種類作成し，
システムに投入していただきます．
In the re-identification phase, you create four re-identification data(Fh) using Tα for one anonymous data, and submit them.
	F25_***Anonymise Data name***.txt
	F50_***Anonymise Data name***.txt
	F75_***Anonymise Data name***.txt
	F100_***Anonymise Data name***.txt

・システム側では，Tαを用いていないデータの排除等を行うことはありませんが，
上位チームに対しては，個別にデータを解析し，実行委員から質問が来る場合があります．
On the system side, we will not eliminate data that does not use Tα,
For upper teams, data may be individually analyzed and questions may come from executive committee members.




