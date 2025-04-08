"""
إصلاح قالب صفحة 'حول عنا' (about_us_django.html) لدعم اللغتين العربية والإنجليزية
"""

def fix_about_us_template():
    with open('templates/about_us_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث نص المهمة
    content = content.replace(
        '<p class="card-text">في كاررنتال، نلتزم بتوفير تجارب استثنائية لتأجير المركبات من خلال خدمة متميزة، وأسطول متنوع من المركبات عالية الجودة، وتكنولوجيا مبتكرة تبسط عملية التأجير.</p>',
        '<p class="card-text">{% if is_english %}At CarRental, we are committed to providing exceptional vehicle rental experiences through outstanding service, a diverse fleet of high-quality vehicles, and innovative technology that simplifies the rental process.{% else %}في كاررنتال، نلتزم بتوفير تجارب استثنائية لتأجير المركبات من خلال خدمة متميزة، وأسطول متنوع من المركبات عالية الجودة، وتكنولوجيا مبتكرة تبسط عملية التأجير.{% endif %}</p>'
    )
    
    content = content.replace(
        '<p class="card-text">نحن نؤمن بأن التنقل يجب أن يكون متاحاً وملائماً وممتعاً. مهمتنا هي تمكين عملائنا من حرية الاستكشاف والتواصل وتحقيق أهدافهم من خلال حلول نقل موثوقة.</p>',
        '<p class="card-text">{% if is_english %}We believe mobility should be accessible, convenient, and enjoyable. Our mission is to empower our customers with the freedom to explore, connect, and achieve their goals through reliable transportation solutions.{% else %}نحن نؤمن بأن التنقل يجب أن يكون متاحاً وملائماً وممتعاً. مهمتنا هي تمكين عملائنا من حرية الاستكشاف والتواصل وتحقيق أهدافهم من خلال حلول نقل موثوقة.{% endif %}</p>'
    )
    
    # تحديث عنوان القيم
    content = content.replace(
        '<h3 class="h5 mt-4 mb-3">قيمنا</h3>',
        '<h3 class="h5 mt-4 mb-3">{% if is_english %}Our Values{% else %}قيمنا{% endif %}</h3>'
    )
    
    # تحديث نصوص القيم (البحث عن الفقرات الأخرى وتحديثها)
    
    # تحديث عنوان التاريخ
    content = content.replace(
        '<h2 class="card-title mb-4">تاريخنا</h2>',
        '<h2 class="card-title mb-4">{% if is_english %}Our History{% else %}تاريخنا{% endif %}</h2>'
    )
    
    # تحديث مقاطع التاريخ
    content = content.replace(
        '<p class="card-text">بدأت كاررنتال كشركة صغيرة في عام 2010 بفكرة بسيطة: توفير خدمة تأجير سيارات ممتازة بأسعار معقولة. تأسست الشركة على يد مجموعة من رواد الأعمال الشغوفين بالسيارات وخدمة العملاء.</p>',
        '<p class="card-text">{% if is_english %}CarRental started as a small company in 2010 with a simple idea: providing excellent car rental service at reasonable prices. The company was founded by a group of entrepreneurs passionate about cars and customer service.{% else %}بدأت كاررنتال كشركة صغيرة في عام 2010 بفكرة بسيطة: توفير خدمة تأجير سيارات ممتازة بأسعار معقولة. تأسست الشركة على يد مجموعة من رواد الأعمال الشغوفين بالسيارات وخدمة العملاء.{% endif %}</p>'
    )
    
    content = content.replace(
        '<p class="card-text">من خلال التركيز على تقديم تجربة استثنائية للعملاء والاستثمار في أحدث التقنيات، نمت الشركة بسرعة لتصبح واحدة من الشركات الرائدة في مجال تأجير السيارات في المنطقة.</p>',
        '<p class="card-text">{% if is_english %}By focusing on providing an exceptional customer experience and investing in the latest technologies, the company quickly grew to become one of the leading car rental companies in the region.{% else %}من خلال التركيز على تقديم تجربة استثنائية للعملاء والاستثمار في أحدث التقنيات، نمت الشركة بسرعة لتصبح واحدة من الشركات الرائدة في مجال تأجير السيارات في المنطقة.{% endif %}</p>'
    )
    
    # تحديث عنوان فريقنا
    content = content.replace(
        '<h2 class="section-title text-center mb-5">فريقنا</h2>',
        '<h2 class="section-title text-center mb-5">{% if is_english %}Our Team{% else %}فريقنا{% endif %}</h2>'
    )
    
    # تحديث نص الاستعداد للمساعدة
    content = content.replace(
        '<p class="lead text-center mb-5">فريقنا من المتخصصين ذوي الخبرة على استعداد لمساعدتك في اختيار السيارة المثالية ومساعدتك في كل خطوة من رحلة التأجير.</p>',
        '<p class="lead text-center mb-5">{% if is_english %}Our team of experienced specialists is ready to help you choose the perfect car and assist you every step of the way on your rental journey.{% else %}فريقنا من المتخصصين ذوي الخبرة على استعداد لمساعدتك في اختيار السيارة المثالية ومساعدتك في كل خطوة من رحلة التأجير.{% endif %}</p>'
    )
    
    # تحديث عنوان موقعنا
    content = content.replace(
        '<h2 class="section-title text-center mb-5">موقعنا</h2>',
        '<h2 class="section-title text-center mb-5">{% if is_english %}Our Location{% else %}موقعنا{% endif %}</h2>'
    )
    
    # تحديث عنوان اتصل بنا
    content = content.replace(
        '<h2 class="section-title text-center mb-5" id="contact">اتصل بنا</h2>',
        '<h2 class="section-title text-center mb-5" id="contact">{% if is_english %}Contact Us{% else %}اتصل بنا{% endif %}</h2>'
    )
    
    # تحديث نص الاتصال
    content = content.replace(
        '<p class="lead text-center mb-5">لديك استفسارات؟ نحن هنا للمساعدة! تواصل معنا من خلال أي من قنوات الاتصال أدناه.</p>',
        '<p class="lead text-center mb-5">{% if is_english %}Have questions? We\'re here to help! Contact us through any of the communication channels below.{% else %}لديك استفسارات؟ نحن هنا للمساعدة! تواصل معنا من خلال أي من قنوات الاتصال أدناه.{% endif %}</p>'
    )
    
    # تحديث عناوين بطاقات الاتصال
    content = content.replace(
        '<h3 class="h5 mb-3">العنوان</h3>',
        '<h3 class="h5 mb-3">{% if is_english %}Address{% else %}العنوان{% endif %}</h3>'
    )
    
    content = content.replace(
        '<h3 class="h5 mb-3">البريد الإلكتروني</h3>',
        '<h3 class="h5 mb-3">{% if is_english %}Email{% else %}البريد الإلكتروني{% endif %}</h3>'
    )
    
    content = content.replace(
        '<h3 class="h5 mb-3">الهاتف</h3>',
        '<h3 class="h5 mb-3">{% if is_english %}Phone{% else %}الهاتف{% endif %}</h3>'
    )
    
    content = content.replace(
        '<h3 class="h5 mb-3">ساعات العمل</h3>',
        '<h3 class="h5 mb-3">{% if is_english %}Working Hours{% else %}ساعات العمل{% endif %}</h3>'
    )
    
    # تحديث النصوص في بطاقات الاتصال
    content = content.replace(
        '<p>الرياض - طريق الملك فهد<br>المملكة العربية السعودية</p>',
        '<p>{% if is_english %}Riyadh - King Fahd Road<br>Saudi Arabia{% else %}الرياض - طريق الملك فهد<br>المملكة العربية السعودية{% endif %}</p>'
    )
    
    content = content.replace(
        '<p>من الأحد إلى الخميس: 9:00 صباحًا - 9:00 مساءً<br>الجمعة والسبت: 10:00 صباحًا - 6:00 مساءً</p>',
        '<p>{% if is_english %}Sunday to Thursday: 9:00 AM - 9:00 PM<br>Friday and Saturday: 10:00 AM - 6:00 PM{% else %}من الأحد إلى الخميس: 9:00 صباحًا - 9:00 مساءً<br>الجمعة والسبت: 10:00 صباحًا - 6:00 مساءً{% endif %}</p>'
    )
    
    # حفظ التغييرات
    with open('templates/about_us_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تحديث قالب صفحة 'حول عنا' بنجاح")

if __name__ == "__main__":
    fix_about_us_template()
