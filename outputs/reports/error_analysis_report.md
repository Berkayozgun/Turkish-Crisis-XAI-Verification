# Model Hata Analizi Raporu (False Positives & False Negatives)

Bu rapor, şampiyon baseline modeli (Logistic Regression) tarafından yanlış sınıflandırılan örnekleri inceleyerek modelin dilsel veya bağlamsal zayıflıklarını ortaya çıkarmayı hedefler.

## 1. False Negatives (Gözden Kaçan Krizler)
**Tanım:** Gerçekte kriz/yardım çağrısı olan ancak model tarafından 'Gürültü/Normal' sanılan tweetler.

- **[maden_2024]**: hedef şaşırtmalarına yardımcı olmayalım."
- **[deprem]**: kalsam evdeki yatak bile batıyor."
- **[maden_2024]**: başka konular konuşulsun istiyorlar Reis."
- **[sarachane]**: Savcı istedi diyecekler. Kurgu devam ediyor."
- **[maden_2024]**: 480 milyon dolarlık teşvik düzenlemesi. Emekli maaşları"
- **[deprem]**: bir milletine el veremedi. Sıfırlanan kurumların en başındaki yerini kimseye kaptırmıyor."
- **[deprem]**: Diyanet'in personeli daha müsait. Aynı amaca hizmet edecekse ne sakıncası var?"
- **[maden_2024]**: hayat pahalılığımı konuşulmalıydı yoksa proje gündem mi"
- **[maden_2024]**: alım değerinin 3 katı durumunda!"" Anahtar Tv Youtube"
- **[maden_2024]**: YENİ FALAN DERKEN YAPILMAK İSTENEN ORTAÇAĞ ANAYASASI İLE NEO SUUDİ ARABİSTAN OLMAKTAN KURTULABİLECEK Mİ TÜRKİYE SORUNSALI? Çalık'ın tankerleriyle IŞID petrolü taşıyarak İsrail'e ve Koç'un Tüpraş'ına satanları gördü Türkiye. Üniversitelerdeki akademik kadrolar dahil olmak

## 2. False Positives (Yanlış Alarmlar)
**Tanım:** Gerçekte gündelik (gürültü) olan ancak model tarafından 'Kriz' olarak işaretlenen tweetler.

- **[noise]**: KAMPANYALI VE INDIRIMLI ÜRÜNLERIMI KAÇIRMAMAK IÇIN TAKIPTE KALIN ?
- **[noise]**: ılık esen havada deniz sesi, kokusu ve rum ezgileri eşliğinde malum masada bulunma ihtiyacı hasıl oldu yine. bilen bilir bu dayanılmaz istek; iflas etmek üzere olan bünyenin, ruhuna ilk yardım çağrısıdır
- **[noise]**: O renklerle kararmssin zaten daha fazla kararmak istiyorsan sirani bekle can emre ????????
- **[noise]**: gulce.story Nitelikli dolandiriciliga giriyor bu yahu ?????
- **[noise]**: alexander010154Reis bu sefer gerçekten gazi oldun
- **[noise]**: kendi çocuklarını ve torunlarını vakıflara göndermiyorlar... ailemizde eşcinsel istemiyoruz politikası mı veya politikada önümü kapama bakış açısı mı anlamadım
- **[noise]**: alisanofficial aferin kendi bokunu yemis
- **[noise]**: Dünya üzerinde bir suriyeli bir filistinli bir rohingyalı bir doğu türkistanlı mağdur olduğu zaman adalet isteyecek gücün yoksa kalkıp sivasta teröriste istediğin şey adalet değildir terör seviciliktir
- **[noise]**: kennderr Liet me think ??
- **[noise]**: Rus muhalif ın senelerdir hangi hapishanede tutulduğu bilinmiyordu. Bizde terör örgütü başı krallar gibi hapis yatıyor bir eli balda bir eli yağda bu muhalefet Avrupada olsa 1 saat gezebilirlerdi artık Devlet sert yüzünü göstermeli.
