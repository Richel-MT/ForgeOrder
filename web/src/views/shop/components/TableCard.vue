<template>
    <mdui-card class="table-card" variant="outlined">
            <div>
                <div class="table-card-title-container">
                    <div class="table-card-title">{{ props.name }}</div>
                    <div class="table-card-subtitle" v-if="!props.isAvailable">(已禁用)</div>
                </div>
                <div class="table-card-status">
                    
                    <div class="table-card-status-circle free-color"></div>
                    <!-- <mdui-circular-progress style="width: 20px; height: 20px"></mdui-circular-progress> -->
                    空闲
                </div>
            </div>

            <div class="table-card-actions">
                <mdui-button-icon @click="editName">
                    <mdui-icon-edit></mdui-icon-edit>
                </mdui-button-icon>

                <mdui-button-icon @click="deleteTable">
                    <mdui-icon-clear></mdui-icon-clear>
                </mdui-button-icon>
            </div>
            
    </mdui-card>

</template>

<script setup>

    import 'mdui/components/card.js'
    import 'mdui/components/button-icon.js'
    import 'mdui/components/circular-progress.js'
    import { prompt } from 'mdui/functions/prompt.js'
    import { t } from '@/locales/index.js'
    import { snackbar } from 'mdui/functions/snackbar.js'
    import { dialog } from 'mdui/functions/dialog.js';
 
    import '@mdui/icons/edit.js'
    import '@mdui/icons/clear.js'

    import request from '@/utils/request'
    
    const emit = defineEmits(['reload'])

    const props = defineProps({
        "id": {
            type: Number
        },
      "name": {
        type: String
      },
      "isAvailable": {
        type: Boolean
      }
    })



    const editName = () => {
        prompt({
            headline: t("shop.tables.edit_name.headline", {name: props.name}),
            description: t("shop.tables.edit_name.description"),
            confirmText: t("common.text.confirm"),
            cancelText: t("common.text.cancel"),
            onConfirm: async (name) => {
                if (name == "") {
                    snackbar({
                        message: t("shop.tables.edit_name.error.empty"),
                        duration: 2000
                    })
                    return
                }
                const res = await request.post('/shop/tables/update', {
                    id: props.id,
                    name: name,
                })

                if (res.data.status == 0) {
                    snackbar({
                        message: t("shop.tables.edit_name.success"),
                    })
                    emit('reload')
                } else if (res.data.status == 3001) {
                    snackbar({
                        message: t("shop.tables.edit_name.error.already_exist", {name: name}),
                    })
                }
            }
        })
    }

    
    const deleteTable = () => {
        dialog({
            headline: t("shop.tables.delete_table.headline", {name: props.name}),
            description: t("shop.tables.delete_table.description", {name: props.name}),
            actions : [
                {
                    "text": t("common.text.cancel")
                },
                {
                    "text": t("common.text.confirm"),
                    onClick: async () => {
                const res = await request.post('/shop/tables/delete', {
                    id: props.id,
                })
                if (res.data.status == 0) {
                    snackbar({
                        message: t("shop.tables.delete_table.success"),
                    })
                    emit('reload')
                }
            }
                }
            ]
            
        })
    }
</script>

<style>


.table-card {
    /* width: 180px; */
    /* margin-bottom: 20px; */
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.table-card-title-container {
    display: flex;
    align-items:center;
}

.table-card-title {
    font-size: 24px;
}

.table-card-subtitle {
    font-size: 14px
}

.table-card-status {
    font-size: 16px;
    display: flex;
    gap: 8px;
    align-items: center;
}

.table-card-status-circle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #009688;
}


.free-color {
    background-color: #02c202;
}

.occupied-color {
    background-color: #ff0000;
}

.table-card-actions {
    display: flex;
    flex-direction: column;
    /* gap: 8px */
    
}
</style>