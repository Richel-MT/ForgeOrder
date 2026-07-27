<template>
    <div class="mdui-prose container">
        <h2>{{ $t("shop.title.tables") }}</h2>

        <div class="tables-container">
            <div v-for="table in tables" :key="table.id" :table="table" >
                <TableCard 
                :name="table.name" 
                :is_available="!!table.is_available" 
                :id="table.id"
                @reload="onReload"/>
            </div>
        </div>
        
    </div>
</template>

<script setup>
import TableCard from './components/TableCard.vue'
import request from '@/utils/request.js'

import { ref, onMounted, inject, onBeforeUnmount, h } from 'vue'

import { prompt } from 'mdui/functions/prompt.js'
import { snackbar } from 'mdui/functions/snackbar.js'

import { t } from '@/locales/index.js' 

import '@mdui/icons/add.js';


const tables = ref([])

const { addRightComponent, clearRightComponent } = inject('rightComponent')


const loadTables = async () => {
    const res = await request.get('/shop/tables/getAll')
    
    if (res.data.status == 0) {
        tables.value = res.data.data
    }
}

const createTable = () => {
    prompt({
        headline: t("shop.tables.create_table.headline"),
        description: t("shop.tables.create_table.description"),
        confirmText: t("common.text.confirm"),
        cancelText: t("common.text.cancel"),
        onConfirm: async (name) => {
            if (name == "") {
                snackbar({
                    message: t("shop.tables.create_table.error.empty"),
                })
                return
            }
            const res = await request.post('/shop/tables/new', {
                name: name,
            })

            if (res.data.status == 0) {
                snackbar({
                    message: t("shop.tables.create_table.success"),
                })
                loadTables()
            }
        }
    })
}

onMounted( async () => {
    

    addRightComponent(h('mdui-button-icon', {
        onClick: createTable,
    }, [
        h('mdui-icon-add')
    ]))

    loadTables()

})

const onReload = () => {
    loadTables()
}

onBeforeUnmount(() => {
    clearRightComponent()
})



</script>

<style>

.tables-container {
    display: grid;
    /* flex-wrap: wrap; */
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
}
</style>