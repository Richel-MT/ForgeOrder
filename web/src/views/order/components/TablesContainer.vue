<template>
    <div class="tables-container">
        <div v-for="table in tables" :key="table.id" :table="table" >
            <mdui-card class="table-card" variant="outlined" clickable @click="handleClick(table)">
                <div>
                    <div class="table-card-title-container">
                        <div class="table-card-title">{{ table.name }}</div>
                        <div class="table-card-subtitle" v-if="!table.isAvailable">(已禁用)</div>
                    </div>
                    <div class="table-card-status">
                        
                        <div class="table-card-status-circle free-color"></div>
                        <!-- <mdui-circular-progress style="width: 20px; height: 20px"></mdui-circular-progress> -->
                        空闲
                    </div>
                </div>

                <div class="table-card-actions" v-if="selectedTable == table.id">
                    <mdui-icon-done></mdui-icon-done>         
            </div>

            </mdui-card>
        </div>
    </div>

</template>

<script setup>

    import 'mdui/components/card.js'
    import 'mdui/components/button-icon.js'
    import 'mdui/components/circular-progress.js'

    import '@mdui/icons/done.js';
 
    import { ref } from 'vue'

    const props = defineProps({
        "tables": {
            type: Array,
            default: []
        },
      "modelValue": {
        type: Number,
        default: -1
      }
    })

    const emit = defineEmits(['click', 'update:modelValue'])

    const selectedTable = ref(props.modelValue)

    const handleClick = (table) => {
        selectedTable.value = table.id

        emit('update:modelValue', selectedTable.value)

        console.log(selectedTable.value)
    }


    
    
</script>

<style>
.tables-container {
    display: grid;
    /* flex-wrap: wrap; */
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
}

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