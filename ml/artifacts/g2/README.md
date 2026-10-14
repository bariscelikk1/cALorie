# G2 Notebook 20 sonuç analizi

Kullanıcının calorie_g2_pose_model_suite_report.zip dosyası incelendi. 1.971 test penceresinin anahtarları, gerçek etiketleri ve sabit V6-C gate olasılıkları yerel V6-C arşiviyle karşılaştırıldı; tümü eşleşti. Aşağıdaki uçtan uca metrikler tahmin CSV'lerinden yeniden hesaplandı.

| Sistem | Macro F1 | Accuracy |
| --- | ---: | ---: |
| V6-C TCN referans | %79,33 | %82,90 |
| V6-C gate + BiGRU | %81,14 | %82,50 |
| V6-C gate + eşit ensemble | %80,72 | %83,00 |
| V6-C gate + Pose Transformer | %78,87 | %82,45 |
| V6-C gate + Adaptive GCN | %77,70 | %82,14 |

BiGRU yeni tekil adaylar arasında doğrulama sınıflandırıcı Macro F1'de de ilk: %89,92; Transformer %89,19; Adaptive GCN %82,53. Bu doğrulama ölçümü gate dahil uçtan uca ölçüm değildir. Ensemble'ın raporlanan %87,22 validation değeri gerçek ensemble tahminlerinden hesaplanmamış, tekil puanların ortalaması yazılmıştır; geçerli ensemble doğrulama metriği olarak kullanılmamalıdır. Arşivde doğrulama tahminleri bulunmadığı için yalnız bu ZIP ile düzeltilemez. Test ensemble Macro F1 değeri CSV'den doğrulandı.

BiGRU'nun V6-C'ye göre Macro F1 artışı 1,81 yüzde puandır. Ancak lat_pulldown F1'i %72,73'ten %100'e çıkmıştır ve bu sınıfta yalnız 7 test penceresi vardır. Bu tek sınıfın eşit ağırlıklı 15 sınıf ortalamasına katkısı yaklaşık +1,82 puandır; diğer sınıfların net katkısı yaklaşık sıfırdır. Dolayısıyla artış geniş tabanlı veya sağlam bir genelleme kazancı olarak sunulmamalıdır. Bench press F1 artarken bicep curl, deadlift ve pull-up F1 gerilemiştir. Pull-up yalnız 4, deadlift 13 ve bench press 19 pencere içerir; pencereler bağımsız kişiler sayılmaz.

Unknown recall tüm sistemlerde %74,58; gate sabit olduğu için unknown reddi iyileşmemiştir. Her model aynı unknown kararlarını verir.

BiGRU en iyi doğrulama sonucunu 2. turda, toplam 8 turda elde etti. Transformer 30 tur çalıştı (en iyi 28), Adaptive GCN 23 tur (en iyi 17). Süre ölçümü arşivden doğrulanmadı.

Karar: BiGRU bağımsız kişi/kaynak doğrulamasına alınacak adaydır; V6-C otomatik olarak değiştirilmemeli. Ensemble BiGRU'yu Macro F1'de geçmedi ve gerçek validation metriği eksik. Yeni kişi/kaynak değerlendirmesinde sınıf kapsamı ve zaman etiketi kalitesi doğrulanmalı. Test sonuçları üzerinden yeni ensemble ağırlığı veya hiperparametre seçilmemeli.

Sınıf bazlı F1 ve recall değerleri G2_CLASS_COMPARISON.csv dosyasındadır. Bu analizde model eğitimi, checkpoint yükleme veya GitHub değişikliği yapılmadı.
