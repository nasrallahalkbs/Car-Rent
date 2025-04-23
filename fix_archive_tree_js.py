"""
إصلاح كود JavaScript لشجرة المجلدات وإضافة سجلات تصحيح
"""

import os

def fix_archive_tree_js():
    """تحديث كود JavaScript في قالب الأرشيف"""
    template_path = "templates/admin/archive/archive_main.html"
    
    # قراءة محتوى الملف
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن بداية سكريبت jQuery
    jquery_script_start = content.find('$(document).ready(function() {')
    if jquery_script_start == -1:
        print("لم يتم العثور على كود jQuery في القالب")
        return
    
    # البحث عن موقع تهيئة jsTree
    jstree_init_start = content.find("$('#folder-tree').jstree({", jquery_script_start)
    if jstree_init_start == -1:
        print("لم يتم العثور على كود تهيئة jsTree في القالب")
        return
    
    # البحث عن نهاية تهيئة jsTree
    jstree_init_end = content.find("});", jstree_init_start)
    if jstree_init_end == -1:
        print("لم يتم العثور على نهاية كود تهيئة jsTree في القالب")
        return
    
    # استخراج بداية محتوى jQuery
    jquery_content_start = content[jquery_script_start:jstree_init_start]
    
    # إضافة سجلات تصحيح قبل تهيئة jsTree
    updated_jquery_content = jquery_content_start.replace(
        'let treeData = {{ folder_tree|safe }};',
        '''// إضافة سجلات تصحيح
        console.log("تهيئة صفحة الأرشيف الإلكتروني...");
        
        // استخدام البيانات من الخادم مباشرة
        let treeData = {{ folder_tree|safe }};
        console.log("بيانات الشجرة المستلمة:", treeData);
        
        // إذا لم تكن البيانات متاحة، استخدم بيانات افتراضية للاختبار
        if (!treeData || treeData.length === 0) {
            console.log("لا توجد بيانات للشجرة، استخدام بيانات افتراضية للاختبار...");
            treeData = [
                {
                    'id': 'recycle-bin',
                    'text': 'سلة المحذوفات',
                    'icon': 'fas fa-trash-alt',
                    'type': 'system',
                    'state': { 'opened': false }
                },
                {
                    'id': 27,
                    'text': 'تصميم (شجرة)',
                    'icon': 'fas fa-folder',
                    'type': 'folder',
                    'state': { 'opened': true },
                    'children': [
                        {
                            'id': 28,
                            'text': 'رسوم (1)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 29,
                            'text': 'حضور (2)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 30,
                            'text': 'حسابات (3)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 31,
                            'text': 'محفوظات (4)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 32,
                            'text': 'توكيلات (5)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        }
                    ]
                }
            ];
        }'''
    )
    
    # تحديث محتوى تهيئة jsTree
    jstree_init_content = content[jstree_init_start:jstree_init_end+3]
    
    updated_jstree_init = jstree_init_content.replace(
        "'core' : {",
        """'core' : {
                'animation': 100,
                'check_callback': true,"""
    )
    
    # استخراج محتوى ما بعد تهيئة jsTree
    after_jstree_init = content[jstree_init_end+3:]
    
    # إضافة سجلات تصحيح بعد تهيئة jsTree
    updated_after_jstree = after_jstree_init.replace(
        ".on('ready.jstree', function() {",
        """.on('ready.jstree', function() {
            console.log("تم تهيئة شجرة المجلدات بنجاح");"""
    ).replace(
        ".on('select_node.jstree', function(e, data) {",
        """.on('select_node.jstree', function(e, data) {
            console.log("تم تحديد مجلد:", data.node.id, data.node.text);"""
    )
    
    # تجميع المحتوى المحدث
    updated_content = jquery_content_start.replace(
        'let treeData = {{ folder_tree|safe }};',
        '''// إضافة سجلات تصحيح
        console.log("تهيئة صفحة الأرشيف الإلكتروني...");
        
        // استخدام البيانات من الخادم مباشرة
        let treeData = {{ folder_tree|safe }};
        console.log("بيانات الشجرة المستلمة:", treeData);
        
        // إذا لم تكن البيانات متاحة، استخدم بيانات افتراضية للاختبار
        if (!treeData || treeData.length === 0) {
            console.log("لا توجد بيانات للشجرة، استخدام بيانات افتراضية للاختبار...");
            treeData = [
                {
                    'id': 'recycle-bin',
                    'text': 'سلة المحذوفات',
                    'icon': 'fas fa-trash-alt',
                    'type': 'system',
                    'state': { 'opened': false }
                },
                {
                    'id': 27,
                    'text': 'تصميم (شجرة)',
                    'icon': 'fas fa-folder',
                    'type': 'folder',
                    'state': { 'opened': true },
                    'children': [
                        {
                            'id': 28,
                            'text': 'رسوم (1)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 29,
                            'text': 'حضور (2)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 30,
                            'text': 'حسابات (3)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 31,
                            'text': 'محفوظات (4)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        },
                        {
                            'id': 32,
                            'text': 'توكيلات (5)',
                            'icon': 'fas fa-folder',
                            'type': 'folder'
                        }
                    ]
                }
            ];
        }'''
    ) + updated_jstree_init.replace(
        "'core' : {",
        """'core' : {
                'animation': 100,
                'check_callback': true,"""
    ) + updated_after_jstree.replace(
        ".on('ready.jstree', function() {",
        """.on('ready.jstree', function() {
            console.log("تم تهيئة شجرة المجلدات بنجاح");"""
    ).replace(
        ".on('select_node.jstree', function(e, data) {",
        """.on('select_node.jstree', function(e, data) {
            console.log("تم تحديد مجلد:", data.node.id, data.node.text);"""
    )
    
    # حفظ الملف المحدث
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث كود JavaScript لشجرة المجلدات بنجاح")

if __name__ == "__main__":
    fix_archive_tree_js()