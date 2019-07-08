INSERT INTO `trainingdata`(`id`, `text`, `chapter_idx`, `chapter_number`, `header`, `header_preprocessed`, `parent_header`, `parent_preprocessed`, `grandparent_header`, `grandparent_preprocessed`, `topic_1_id`, `topic_1_value`, `topic_2_id`, `topic_2_value`, `topic_3_id`, `topic_3_value`, `topic_4_id`, `topic_4_value`, `topic_5_id`, `topic_5_value`, `document_id`, `label`, `createdAt`, `updatedAt`)
SELECT * from ((
            select *, 1 as 'label', CURRENT_TIME() as createdAt, CURRENT_TIME() as updatedAt
            from chapter
            where topic_1_id = 9
            limit 500
        )
        union
        (
            select *, 0 as 'label', CURRENT_TIME() as createdAt, CURRENT_TIME() as updatedAt
            from chapter
            where topic_1_id != 9
            limit 500
        )) as a